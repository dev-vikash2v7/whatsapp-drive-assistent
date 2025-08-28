import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from twilio.twiml.messaging_response import MessagingResponse
from google.oauth2.credentials import Credentials

from utils.command_parser import CommandParser
from utils.google_drive_client import GoogleDriveClient
from utils.document_summarizer import DocumentSummarizer

from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

command_parser = CommandParser()
drive_client = GoogleDriveClient()

summarizer = DocumentSummarizer()



    

@app.route("/api/auth", methods=["POST"])
def auth():
    data = request.json
    code = data.get("code")
    whatsapp_number = data.get("whatsapp_number")
    
    if not code:
        return jsonify({"success": False, "error": "Authorization code is required"}), 400
    
    if not whatsapp_number:
        return jsonify({"success": False, "error": "WhatsApp number is required"}), 400
    
    try:
        drive_client._authenticate(code, whatsapp_number)

        return jsonify({"success": True, "message": "Connected to Google Drive"})
    except Exception as e:
        print(f"Authentication failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500




@app.route('/api/webhook', methods=['POST'])
def api_incoming_message():
    try:
        message_body = request.form.get("Body")
        message_sid = request.form.get("MessageSid")
        from_number = request.form.get("From")
        # data = request.get_json()
        
        print("api_execute" , from_number , message_body , message_sid)

        if not message_body:
            return _create_twilio_response("No message provided")
        
        # Set the WhatsApp number in the command parser for authentication
        command_parser.current_whatsapp_number = from_number
        
        # Parse the command
        parsed_command = command_parser.parse_message(message_body)
        
        if not parsed_command.get("success", False):
           return _create_twilio_response("Command not found")
        
        command = parsed_command.get("command")

        response_text = _execute_command(command, parsed_command)
        print("response_text" , response_text)

        
        return _create_twilio_response(response_text)
        
    except Exception as e:
        print(f"Error in API execute: {e}")
        # return _create_twilio_response(str(e))
        return _create_twilio_response(str(e))





@app.route('/api/execute', methods=['POST'])
def api_execute():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        message_body = data.get('message', '')
        if not message_body:
            return jsonify({"error": "No message provided"}), 400
        
        # Parse the command
        parsed_command = command_parser.parse_message(message_body)
        
        if not parsed_command.get("success", False):
            return jsonify({
                "success": False,
                "error": parsed_command.get("error", "Unknown error"),
                "response": command_parser.format_response(parsed_command),

            })
        
        command = parsed_command.get("command")

        response_text = _execute_command(command, parsed_command)

        
        print("response_text" , response_text)

        
        return jsonify({
            "success": True,
            "command": command,
            "response": response_text, 
        })
        
    except Exception as e:
        print(f"Error in API execute: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500



@app.route('/api/files', methods=['GET'])
def get_files():
    """Get list of files in a folder"""
    try:
        folder_path = request.args.get('folder', '/')
        result = drive_client.list_files(folder_path)
        
        if "error" in result:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 400
        
        return jsonify({
            "success": True,
            "files": result.get("files", [])
        })
        
    except Exception as e:
        print(f"Error getting files: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/files/<path:file_path>', methods=['DELETE'])
def delete_file_api(file_path):
    """Delete a file by path"""
    try:
        result = drive_client.delete_file(f"/{file_path}")
        
        if "error" in result:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 400
        
        return jsonify({
            "success": True,
            "message": result.get("message", "File deleted successfully")
        })
        
    except Exception as e:
        print(f"Error deleting file: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/files/move', methods=['POST'])
def move_file_api():
    """Move a file to a different folder"""
    try:
        data = request.get_json()
        source_path = data.get('source_path')
        destination_path = data.get('destination_path')
        
        if not source_path or not destination_path:
            return jsonify({
                "success": False,
                "error": "Source and destination paths are required"
            }), 400
        
        result = drive_client.move_file(source_path, destination_path)
        
        if "error" in result:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 400
        
        return jsonify({
            "success": True,
            "message": result.get("message", "File moved successfully")
        })
        
    except Exception as e:
        print(f"Error moving file: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/files/copy', methods=['POST'])
def copy_file_api():
    """Copy a file to a different folder"""
    try:
        data = request.get_json()
        source_path = data.get('source_path')
        destination_path = data.get('destination_path')
        
        if not source_path or not destination_path:
            return jsonify({
                "success": False,
                "error": "Source and destination paths are required"
            }), 400
        
        result = drive_client.copy_file(source_path, destination_path)
        
        if "error" in result:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 400
        
        return jsonify({
            "success": True,
            "message": result.get("message", "File copied successfully")
        })
        
    except Exception as e:
        print(f"Error copying file: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/summary/file/<path:file_path>', methods=['GET'])
def get_file_summary_api(file_path):
    """Get summary of a file"""
    try:
        result = summarizer.summarize_single_document(drive_client  , f"/{file_path}")
        formatted_summary = summarizer.format_summary_response(result)
        
        return jsonify({
            "success": True,
            "summary": formatted_summary
        })
        
    except Exception as e:
        print(f"Error getting file summary: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/summary/folder/<path:folder_path>', methods=['GET'])
def get_folder_summary_api(folder_path):
    """Get summary of a folder"""
    try:
        result = summarizer.summarize_folder(drive_client ,f"/{folder_path}")
        formatted_summary = summarizer.format_summary_response(result)
        
        return jsonify({
            "success": True,
            "summary": formatted_summary
        })
        
    except Exception as e:
        print(f"Error getting folder summary: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



def _execute_command(command: str, parsed_command: dict) -> str:
    try:
        # print('command' , command)
        # print('parsed_command' , parsed_command)
        # print(GoogleDriveClient.serv  ice)

     
        whatsapp_number = getattr(command_parser, 'current_whatsapp_number', None)
        
        if not drive_client.service:
            res = drive_client.is_authenticated(whatsapp_number)
            if not res:
                return 'Please first sign in to your google drive account to use this command. Visit http://localhost:3000/ to sign in.'



        if command == "LIST":
            folder_path = parsed_command.get("folder_path")

            result = drive_client.list_files(folder_path)

            # print("list result" , result)
            return _format_list_response(result)
        
        elif command == "DELETE":
            file_path = parsed_command.get("file_path")
            result = drive_client.delete_file(file_path)
            # print("delete result" , result)
            return _format_delete_response(result)
        
        elif command == "MOVE":
            source_path = parsed_command.get("source_path")
            destination_path = parsed_command.get("destination_path")

            print("source_path" , source_path)
            print("destination_path" , destination_path)

            result = drive_client.move_file(source_path, destination_path)
            # print("move result" , result)
            return _format_move_response(result)
        
        elif command == "COPY":
            source_path = parsed_command.get("source_path")
            destination_path = parsed_command.get("destination_path")

            print("source_path" , source_path)
            print("destination_path" , destination_path)


            result = drive_client.copy_file(source_path, destination_path)


            # print("copy result" , result)

            return _format_copy_response(result)
        




        elif command == "FOLDERSUMMARY":
            print('folder summary')

            folder_path = parsed_command.get("folder_path")


            result = summarizer.summarize_folder(drive_client , folder_path)

            formatted_summary = summarizer.format_summary_response(result)

            print("formatted_summary" , formatted_summary)
            
            return formatted_summary

            
        
        elif command == "FILESUMMARY":
            print('file summary')

            file_path = parsed_command.get("file_path")

            result = summarizer.summarize_single_document(drive_client , file_path)

            formatted_summary = summarizer.format_summary_response(result)

            # print("formatted_summary" , formatted_summary)

            return formatted_summary
        
        
        elif command == "HELP":
            text = parsed_command.get("help_text")
            # print("help text" , text)
            return text
        
        else:
            return f"❌ Unsupported command: {command}"
            
    except Exception as e:
        print(f"Error executing command {command}: {e}")
        return f"❌ Error executing command: {str(e)}"





def _format_list_response(result: dict) -> str:
    """Format list files response for WhatsApp"""
    if "error" in result:
        return f"❌ {result['error']}"
    
    if "message" in result and "No files found" in result["message"]:
        return "📁 No files found in the specified folder"
    
    files = result.get("files", [])
    if not files:
        return "📁 No files found"
    
    response = "📁 *Files in folder:*\n\n"
    
    for i, file_info in enumerate(files, 1):
        response += f"{i}. *{file_info['name']}*\n"
        response += f"   📄 Type: {file_info['type']}\n"
        response += f"   📏 Size: {file_info['size']}\n"
        response += f"   📅 Modified: {file_info['modified']}\n\n"
    
    return response



def _format_delete_response(result: dict) -> str:
    if "error" in result:
        return f"❌ {result['error']}"
    
    if "message" in result:
        return f"✅ {result['message']}"
    
    return "✅ File deleted successfully"




def _format_move_response(result: dict) -> str:
    if "error" in result:
        return f"❌ {result['error']}"
    
    if "message" in result:
        return f"✅ {result['message']}"
    
    return "✅ File moved successfully"



def _format_copy_response(result: dict) -> str:
    if "error" in result:
        return f"❌ {result['error']}"
    
    if "message" in result:
        return f"✅ {result['message']}"
    
    return "✅ File copied successfully"






def _create_twilio_response(message: str) -> str:
    resp = MessagingResponse()
    resp.message(message)
    return str(resp)






@app.route('/', methods=['GET'])
def get_root():
    print("get_root")
    return jsonify({
        "message": "WhatsApp Drive Assistant API is running",
        "status": "running"
        })

@app.route('/api/auth/status', methods=['GET'])
def is_authenticated():
    whatsapp_number = request.args.get('whatsapp_number')
    
    if not whatsapp_number:
        return jsonify({"success": False, "error": "WhatsApp number is required"}), 400
    
    is_authenticated = drive_client.is_authenticated(whatsapp_number)

    print("is_authenticated" , is_authenticated)

    return jsonify({"success": True, "authenticated": is_authenticated})

@app.route('/api/disconnect', methods=['POST'])
def disconnect():
    data = request.get_json()
        
    if not data:
        return jsonify({"error": "No data received"}), 400
    
    whatsapp_number = data.get('whatsapp_number')
    
    if not whatsapp_number:
        return jsonify({"success": False, "error": "WhatsApp number is required"}), 400
    
    status = drive_client.disconnect(whatsapp_number)


    return jsonify({"success": status})



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'DEV'
    
    # print(f"Starting WhatsApp Drive Assistant API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
