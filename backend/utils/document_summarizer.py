import os
import json
import logging
from typing import List, Dict, Optional
from utils.google_drive_client import GoogleDriveClient
import google.generativeai as genai



class DocumentSummarizer:
    """AI-powered document summarizer using GEMINI_API_KEY"""
    
    def __init__(self, api_key: str = None):
        
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API key not found")
        
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
        original_proxy_values = {}
        
        for var in proxy_vars:
            if var in os.environ:
                original_proxy_values[var] = os.environ[var]
                del os.environ[var]
        
        try:
            self.client = genai.GenerativeModel("gemini-2.0-flash")

        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            # Restore proxy environment variables if they existed
            for var, value in original_proxy_values.items():
                os.environ[var] = value
            raise
        finally:
            # Restore proxy environment variables if they existed
            for var, value in original_proxy_values.items():
                os.environ[var] = value

    
    def summarize_folder(self, drive_client: GoogleDriveClient, folder_path: str) -> Dict:
        """Generate summaries for all documents in a folder"""
        try:
            # List files in the folder
            files_result = drive_client.list_files(folder_path)

            
            if "error" in files_result:
                return files_result
            
            if "message" in files_result and "No files found" in files_result["message"]:
                return {"message": "No documents found in folder"}
            
            files = files_result.get("files", [])
            summaries = []
            
            # Filter for document types that can be summarized
            document_types = [
                'application/vnd.google-apps.document',
                'application/pdf',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'text/plain'
            ]
            
            document_files = [f for f in files if f['type'] in document_types]
            
            if not document_files:
                return {"message": "No summarizable documents found in folder"}
            
            # Generate summaries for each document
            for file_info in document_files:
                file_path = f"{folder_path}/{file_info['name']}"


                summary = self._summarize_single_document(drive_client , file_path, file_info['name'])
                
                if "error" not in summary:
                    summaries.append({
                        "filename": file_info['name'],
                        "summary": summary['summary'],
                        "word_count": summary['word_count']
                    })
            
            if not summaries:
                return {"error": "Failed to generate any summaries"}
            
            # Create a comprehensive folder summary
            folder_summary = self._create_folder_summary(summaries, folder_path)
            
            return {
                "folder_path": folder_path,
                "total_documents": len(summaries),
                "summaries": summaries,
                "folder_summary": folder_summary
            }
            
        except Exception as e:
            print(f"Error summarizing folder: {e}")
            return {"error": f"Failed to summarize folder: {str(e)}"}
    
    def summarize_single_document(self,drive_client: GoogleDriveClient ,  file_path: str) -> Dict:
        """Generate summary for a single document"""
        try:
            # Get file name from path
            file_name = file_path.split('/')[-1]
            return self._summarize_single_document(drive_client,file_path, file_name)
            
        except Exception as e:
            print(f"Error summarizing document: {e}")
            return {"error": f"Failed to summarize document: {str(e)}"}
    

    
    def _summarize_single_document(self, drive_client: GoogleDriveClient, file_path: str, file_name: str) -> Dict:
        print("""Generate summary for a single document""")
        try:
            # Get document content
            content_result = drive_client.get_document_content(file_path)

            
            if "error" in content_result:
                return content_result
            
            content = content_result['content']
            
            if not content.strip():
                return {"error": f"Document '{file_name}' is empty or could not be read"}
            
            # Truncate content if too long (OpenAI has token limits)
            max_chars = 8000  # Conservative limit
            if len(content) > max_chars:
                content = content[:max_chars] + "\n\n[Content truncated for summarization]"
            
            # Generate summary using OpenAI
            summary = self._generate_ai_summary(content, file_name)
            
            if "error" in summary:
                return summary
            
            return {
                "filename": file_name,
                "summary": summary['summary'],
                "word_count": len(content.split()),
                "original_length": len(content)
            }
            
        except Exception as e:
            print(f"Error in _summarize_single_document: {e}")
            return {"error": f"Failed to summarize document: {str(e)}"}
    



    def _generate_ai_summary(self, content: str, filename: str) -> Dict:
        """Generate AI summary using Google Gemini"""
        try:
            prompt = f"""
            Provide only 1-2 sentence linke short  summary with bullet pointes of the following document: "{filename}"
            
            Document content:
            {content}
            
            """

            response = self.client.generate_content(prompt)
            summary = response.text.strip()

        
            return {"summary": summary}
            
        except Exception as e:
            print(f"Error generating AI summary: {e}")
            return {"error": f"Failed to generate AI summary: {str(e)}"}


    
    def _create_folder_summary(self, summaries: List[Dict], folder_path: str) -> str:
        """Create a comprehensive summary of all documents in the folder"""
        try:
            if not summaries:
                return "No documents to summarize."
            
            # Create a combined summary of all documents
            combined_content = f"Folder: {folder_path}\n\n"
            combined_content += f"Total documents: {len(summaries)}\n\n"
            
            for i, summary_info in enumerate(summaries, 1):
                combined_content += f"{i}. {summary_info['filename']}\n"
                combined_content += f"   {summary_info['summary']}\n\n"
            
            # Generate a high-level folder summary
            prompt = f"""
            Please provide single line very short description of this folder based on the following document summaries:
            
            {combined_content}
            
            """
            
            response = self.client.generate_content(prompt)

            return response.text.strip()
            
        except Exception as e:
            print(f"Error creating folder summary: {e}")
            return f"Folder contains {len(summaries)} documents. Individual summaries available above."

            
    
    def format_summary_response(self, summary_result: Dict) -> str:
        try:
            if "error" in summary_result:
                return f"❌ Error: {summary_result['error']}"
            
            if "message" in summary_result:
                return f"ℹ️ {summary_result['message']}"
            
            # Single document summary
            if "filename" in summary_result and "summary" in summary_result:
                response = f"📄 *{summary_result['filename']}*\n\n"
                response += f"{summary_result['summary']}\n\n"
                return response
            
            # Folder summary
            if "folder_summary" in summary_result:
                response = f"📁 *{summary_result['folder_path']} Folder*\n\n"
                response += f"📊 Total documents: {summary_result['total_documents']}\n\n"
                response += f"📋 *Folder Overview:*\n{summary_result['folder_summary']}\n\n"
                
                response += "📄 *Document Summaries:*\n"
                for i, doc_summary in enumerate(summary_result['summaries'], 1):
                    response += f"\n{i}. *{doc_summary['filename']}*\n"
                    response += f"{doc_summary['summary']}\n"
                
                return response
            
            return "❌ Unexpected response format"
            
        except Exception as e:
            print(f"Error formatting summary response: {e}")
            return f"❌ Error formatting response: {str(e)}"
