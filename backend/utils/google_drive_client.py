import os
import io
import json
from typing import List, Dict, Optional, Tuple
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
import base64
from docx import Document
import PyPDF2
from bs4 import BeautifulSoup
from datetime import datetime
from google_auth_oauthlib.flow import Flow
from .storage import storage
from .config import Config


class GoogleDriveClient:
    
    service = None
    current_whatsapp_number = None

    SCOPES = [
      "https://www.googleapis.com/auth/drive.appdata", "https://www.googleapis.com/auth/drive.file",
       "https://www.googleapis.com/auth/drive" , "https://www.googleapis.com/auth/drive.metadata.readonly", "https://www.googleapis.com/auth/userinfo.email", "openid" ,  "https://www.googleapis.com/auth/userinfo.profile" ,"https://www.googleapis.com/auth/drive.readonly"
    ]
    def __init__(self, credentials_file: str = None):
        self.credentials_file =  os.getenv('GOOGLE_DRIVE_CREDENTIALS_FILE')
    
    def signIn(self, code: str, whatsapp_number: str):
        try:
            flow = Flow.from_client_secrets_file(
                        self.credentials_file, scopes=self.SCOPES, redirect_uri=Config.GOOGLE_DRIVE_REDIRECT_URI
                    )

                    
            flow.fetch_token(code=code)

            creds = flow.credentials

            print('creds' , creds)
                    
            try:
                # Save token to persistent storage with WhatsApp number
                token_data = json.loads(creds.to_json())
                storage.save_token(token_data, whatsapp_number)
                self.current_whatsapp_number = whatsapp_number
            except Exception as e:
                print(f"Failed to save token for WhatsApp number {whatsapp_number}: {e}")

            return creds


        except Exception as e:
            print(f"Failed to build Drive self.service: {e}")
            print("Failed to build Drive self.service: " , e)
            raise ValueError(f"Failed to initialize Google Drive self.service: {str(e)}")
        



    def disconnect(self, whatsapp_number: str) -> bool:
        try:
            storage.delete_token(whatsapp_number)
            if self.current_whatsapp_number == whatsapp_number:
                self.current_whatsapp_number = None
                self.service = None
            print(f"Disconnected and token deleted for WhatsApp number: {whatsapp_number}")
            return True
        except Exception as e:
            print(f"Failed to disconnect for WhatsApp number {whatsapp_number}: {e}")
            return False


    def _authenticate(self, code: str, whatsapp_number: str):
        """Authenticate with Google Drive API"""
        try:
            creds = None
            
            print("WhatsApp number for authentication: ", whatsapp_number)
            print("code for authentication: ", code)

            if storage.token_exists(whatsapp_number):
                try:
                    # Load token from persistent storage
                    token_data = storage.load_token(whatsapp_number)
                    if token_data:
                        creds = Credentials.from_authorized_user_info(token_data, self.SCOPES)
                    
                    if not creds or not creds.valid:
                        creds = self.signIn(code, whatsapp_number)
                except Exception as e:
                    print(f"Failed to load existing token for WhatsApp number {whatsapp_number}: {e}")
                    creds = None
            else :
                  creds = self.signIn(code, whatsapp_number)
                
            try:
                self.service = build('drive', 'v3', credentials=creds)
                self.current_whatsapp_number = whatsapp_number

                print('self.service' , self.service)


                print(f"Google Drive authentication successful for WhatsApp number: {whatsapp_number}")



            except Exception as e:
                print(f"Failed to build Drive self.service: {e}")
                print("Failed to build Drive self.service: " , e)
                raise ValueError(f"Failed to initialize Google Drive self.service: {str(e)}")
            
        except Exception as e:
            print(f"Authentication failed for WhatsApp number {whatsapp_number}: {e}")
            print("Authentication failed: " , e)
            raise ValueError(f"Google Drive authentication failed: {str(e)}")

    
    def is_authenticated(self, whatsapp_number: str = None):
        # If no WhatsApp number provided, use the current one
        if whatsapp_number is None:
            whatsapp_number = self.current_whatsapp_number
            
        if not whatsapp_number:
            return False
            
        if not storage.token_exists(whatsapp_number):
            return False

        # Load token from persistent storage
        token_data = storage.load_token(whatsapp_number)
        if not token_data:
            return False

        creds = Credentials.from_authorized_user_info(token_data, self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())  # 🔄 Refresh the token
                    # Save refreshed credentials to persistent storage
                    refreshed_token_data = json.loads(creds.to_json())
                    storage.save_token(refreshed_token_data, whatsapp_number)
                except Exception as e:
                    print(f"Token refresh failed for WhatsApp number {whatsapp_number}:", e)
                    return False
            else:
                return False

        # Build the Drive API self.service with valid credentials
        self.service = build('drive', 'v3', credentials=creds)
        self.current_whatsapp_number = whatsapp_number
        return True

    




    def list_files(self, folder_path: str = None) -> List[Dict]:
        """List files in a specific folder or root"""
        try:
            query = "trashed=false"

            
            if folder_path and folder_path != "/":
                # Get folder ID by name
                folder_id = self._get_folder_id(folder_path)
                if folder_id:
                    query += f" and '{folder_id}' in parents"
                else:
                    return {"error": f"Folder '{folder_path}' not found"}
            
            results = self.service.files().list(
                q=query,
                pageSize=50,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)"
            ).execute()

            
            files = results.get('files', [])

            if not files:
                return {"message": "No files found"}
            
            file_list = []
            for file in files:
                file_info = {
                    "name": file['name'],
                    "id": file['id'],
                    "type": file['mimeType'],
                    "size": self._format_size( int(file.get('size', '0'))),
                    "modified": datetime.strptime(file['modifiedTime'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
                }

                file_list.append(file_info)
            
            # print("file_list ----------- " , file_list)
            
            return {"files": file_list}
            
        except HttpError as error:
            print(f"Error listing files: {error}")
            return {"error": f"Failed to list files: {str(error)}"}
    



    def delete_file(self, file_path: str) -> Dict:
        """Delete a file by path"""
        try:
            file_id = self._get_file_id(file_path)

            if not file_id:
                return {"error": f"File '{file_path}' not found"}
            
            self.service.files().delete(fileId=file_id).execute()

         
            return {"message": f"File '{file_path}' deleted successfully"}
            
        except HttpError as error:
            print(f"Error deleting file: {error}")
            return {"error": f"Failed to delete file: {str(error)}"}


    
    def move_file(self, source_path: str, destination_path: str) -> Dict:
        try:
            file_id = self._get_file_id(source_path)
            if not file_id:
                return {"error": f"Source file '{source_path}' not found"}
            
    
            destination_folder_id = self._get_folder_id(destination_path)

            if not destination_folder_id:
                return {"error": f"Destination folder '{destination_path}' not found"}
            
            # Get current parents
            file = self.service.files().get(fileId=file_id, fields='parents').execute()
            previous_parents = ",".join(file.get('parents', []))
            
            # Move the file to the new folder
            file = self.service.files().update(
                fileId=file_id,
                addParents=destination_folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
            
            return {"message": f"File moved from '{source_path}' to '{destination_path}' successfully"}
            
        except HttpError as error:
            print(f"Error moving file: {error}")
            return {"error": f"Failed to move file: {str(error)}"}
    



    def copy_file(self, source_path: str, destination_path: str) -> Dict:
        try:
            file_id = self._get_file_id(source_path)
            if not file_id:
                return {"error": f"Source file '{source_path}' not found"}
            
            destination_folder_id = self._get_folder_id(destination_path)

            if not destination_folder_id:
                return {"error": f"Destination folder '{destination_path}' not found"}
            
            # Get the source file metadata (to preserve name, etc.)
            source_file = self.service.files().get(fileId=file_id, fields='name, mimeType').execute()

            # Create the copy in the destination folder
            copied_file = self.service.files().copy(
            fileId=file_id,
            body={
                'name': source_file['name'],  # Keep original name
                'parents': [destination_folder_id]
            }
            ).execute()

            return {"message": f"File '{source_path}' copied to '{destination_path}' successfully", "file_id": copied_file.get('id')}


        except HttpError as error:
            print(f"Error copying file: {error}")
            return {"error": f"Failed to copy file: {str(error)}"}



    def get_document_content(self, file_path: str) -> Dict:
        """Extract text content from various document types"""
        try:
            file_id = self._get_file_id(file_path)

            if not file_id:
                return {"error": f"File '{file_path}' not found"}
            
            # Get file metadata
            file_metadata = self.service.files().get(fileId=file_id).execute()
            mime_type = file_metadata['mimeType']
            
            content = ""
            
            if mime_type == 'application/vnd.google-apps.document':
                # Google Docs
                content = self._get_google_doc_content(file_id)
            elif mime_type == 'application/pdf':
                # PDF files
                content = self._get_pdf_content(file_id)
            elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                # DOCX files
                content = self._get_docx_content(file_id)
            elif mime_type == 'text/plain':
                # Text files
                content = self._get_text_content(file_id)
            else:
                return {"error": f"Unsupported file type: {mime_type}"}
            
            return {"content": content, "filename": file_metadata['name']}
            
        except HttpError as error:
            print(f"Error getting document content: {error}")
            return {"error": f"Failed to get document content: {str(error)}"}
    
    def _get_google_doc_content(self, file_id: str) -> str:
        """Extract content from Google Docs"""
        try:
            # Export as plain text
            request = self.service.files().export_media(
                fileId=file_id,
                mimeType='text/plain'
            )
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            return fh.getvalue().decode('utf-8')
        except Exception as e:
            print(f"Error extracting Google Doc content: {e}")
            return ""
    
    def _get_pdf_content(self, file_id: str) -> str:
        """Extract text content from PDF"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            pdf_content = fh.getvalue()
            
            # Extract text using PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text
        except Exception as e:
            print(f"Error extracting PDF content: {e}")
            return ""
    
    def _get_docx_content(self, file_id: str) -> str:
        """Extract text content from DOCX"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            docx_content = fh.getvalue()
            
            # Extract text using python-docx
            doc = Document(io.BytesIO(docx_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text
        except Exception as e:
            print(f"Error extracting DOCX content: {e}")
            return ""
    
    def _get_text_content(self, file_id: str) -> str:
        """Extract text content from plain text files"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            return fh.getvalue().decode('utf-8')
        except Exception as e:
            print(f"Error extracting text content: {e}")
            return ""
    





    def _get_folder_id(self, folder_path: str) -> Optional[str]:
        """Get folder ID by name"""
        try:
            # Remove leading slash
            folder_name = folder_path.lstrip('/')
            
            # Search for folder
            results = self.service.files().list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                fields="files(id, name)"
            ).execute()
            
            files = results.get('files', [])
            if files:
                return files[0]['id']
            return None
        except Exception as e:
            print(f"Error getting folder ID: {e}")
            return None
    









    def _get_file_id(self, file_path: str) -> Optional[str]:
        """Get file ID by path"""
        try:


            path_parts = file_path.strip('/').split('/')

            if len(path_parts) < 2:
                return None
            
            folder_name = path_parts[0]
            file_name = path_parts[1]
            
            # Get folder ID
            folder_id = self._get_folder_id(f"/{folder_name}")

            # print(folder_id)

            if not folder_id:
                return None
            
            # Search for file in folder
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and name='{file_name}' and trashed=false",
                fields="files(id, name)"
            ).execute()

            # print('results' , results)
            
            files = results.get('files', [])
            # print("getfileid files" , files)


            if files:
                return files[0]['id']

            return None
        except Exception as e:
            print(f"Error getting file ID: {e}")
            return None
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
