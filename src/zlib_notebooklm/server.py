"""
MCP Server for Z-Library to NotebookLM
"""

import sys
from mcp.server.fastmcp import FastMCP
from .auth import zlibrary_login
from .core import ZLibraryAutoUploader

# Initialize FastMCP
mcp = FastMCP("zlibrary-to-notebooklm")

@mcp.tool()
def zlib_login() -> str:
    """
    Log in to Z-Library (interactive).
    This will open a browser window for the user to log in.
    Returns a status message.
    """
    success = zlibrary_login()
    if success:
        return "Login successful! Session saved."
    else:
        return "Login failed. Please check the logs or try again."

@mcp.tool()
async def zlib_upload(url: str) -> str:
    """
    Download a book from Z-Library and upload it to NotebookLM.
    
    Args:
        url: The Z-Library URL of the book.
        
    Returns:
        JSON string containing the result (notebook_id, status, etc.)
    """
    uploader = ZLibraryAutoUploader()
    
    # Download
    downloaded_file, file_format = await uploader.download_from_zlibrary(url)
    
    if not downloaded_file or not downloaded_file.exists():
        return "Error: Download failed from Z-Library."
        
    # Convert/Process
    final_file = uploader.convert_to_txt(downloaded_file, file_format)
    
    # Upload
    result = uploader.upload_to_notebooklm(final_file)
    
    if result.get("success"):
        return f"Success! Notebook Created. ID: {result.get('notebook_id')}. Title: {result.get('title')}"
    else:
        return f"Error uploading to NotebookLM: {result.get('error')}"

if __name__ == "__main__":
    mcp.run()
