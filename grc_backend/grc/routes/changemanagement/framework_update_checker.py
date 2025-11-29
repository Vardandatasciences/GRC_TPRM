import json
import os
import re
from datetime import datetime
from typing import Optional

import requests


def create_system_prompt(framework_name: str, last_updated_date: str) -> str:
    """Create system prompt for Perplexity API."""
    return f"""You are a GRC (Governance, Risk, and Compliance) framework update tracker.

Your task is to check if the {framework_name} framework has been updated after {last_updated_date}.

CRITICAL: The has_update field should ONLY be true if the latest official update date is AFTER {last_updated_date}.
If the latest update is on or before {last_updated_date}, set has_update to false.

Instructions:
1. Search for the latest official version/update of {framework_name}
2. Find the exact release/publication date of the latest version
3. Compare the latest update date with {last_updated_date}
4. Set has_update to true ONLY if latest_update_date > {last_updated_date}
5. Respond ONLY in the following JSON format (no additional text):

{{
    "framework_name": "{framework_name}",
    "has_update": true or false,
    "latest_update_date": "YYYY-MM-DD",
    "document_url": "official document URL" or null,
    "version": "version number if available",
    "notes": "brief description of changes if updated"
}}

Requirements:
- has_update must be true ONLY if latest_update_date is AFTER {last_updated_date}
- If latest_update_date is same as or before {last_updated_date}, set has_update to false
- document_url must be a DIRECT download link to the PDF/ZIP file (ending in .pdf, .zip, etc.)
- DO NOT provide page URLs - find the actual downloadable document link
- Use only official sources (nist.gov, iso.org, hhs.gov, etc.)
- If no update found or dates are equal/before, set has_update to false and document_url to null

Example date comparison:
- If last_updated_date is 2025-09-13 and latest is 2025-08-27: has_update = false
- If last_updated_date is 2025-08-27 and latest is 2025-09-13: has_update = true"""


def _clean_response_content(content: str) -> str:
    """Remove markdown fences and return raw JSON string."""
    if "```json" in content:
        return content.split("```json", 1)[1].split("```", 1)[0].strip()
    if "```" in content:
        return content.split("```", 1)[1].split("```", 1)[0].strip()
    return content.strip()


def query_perplexity_api(framework_name: str, last_updated_date: str, api_key: str) -> dict:
    """Call Perplexity API and return parsed JSON response."""
    if not api_key:
        raise ValueError("Perplexity API key is required")

    system_prompt = create_system_prompt(framework_name, last_updated_date)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "user",
                "content": (
                    f"{system_prompt}\n\n"
                    f"Check if {framework_name} has been updated after {last_updated_date}. "
                    "Provide the official document download link if updated."
                ),
            }
        ],
        "temperature": 0.2,
        "max_tokens": 1000,
    }

    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers=headers,
        json=payload,
        timeout=45,
    )
    response.raise_for_status()

    result = response.json()
    content = result["choices"][0]["message"]["content"]
    
    # Log raw response for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Perplexity API raw response for {framework_name}: {content[:500]}...")
    
    parsed = json.loads(_clean_response_content(content))
    logger.info(f"Parsed update info: has_update={parsed.get('has_update')}, latest_update_date={parsed.get('latest_update_date')}, document_url={parsed.get('document_url')}")

    # Validate date ordering per business rules
    if parsed.get("has_update") and parsed.get("latest_update_date"):
        try:
            latest_date = datetime.strptime(parsed["latest_update_date"], "%Y-%m-%d").date()
            last_known = datetime.strptime(last_updated_date, "%Y-%m-%d").date()
            if latest_date <= last_known:
                parsed["has_update"] = False
        except ValueError:
            parsed["has_update"] = False

    return parsed


def find_actual_pdf_url(page_url: str, framework_name: str, api_key: str) -> Optional[str]:
    """Use Perplexity to find the actual PDF download link from a page"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "user",
                "content": f"""Find the direct PDF download link for {framework_name} from this page: {page_url}

Requirements:
1. Find the ACTUAL downloadable PDF file link (must end with .pdf)
2. Do NOT return the main page URL
3. Look for links like "Download PDF", "View PDF", or direct .pdf links
4. Return ONLY the direct PDF URL, nothing else
5. If multiple PDFs exist, return the main framework document

Respond with ONLY the PDF URL or "NOT_FOUND" if no direct PDF link exists."""
            }
        ],
        "temperature": 0.1,
        "max_tokens": 200
    }
    
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        pdf_url = result['choices'][0]['message']['content'].strip()
        
        # Clean up the response
        if pdf_url and pdf_url != "NOT_FOUND" and ".pdf" in pdf_url.lower():
            # Remove any markdown or extra text
            if "http" in pdf_url:
                # Extract just the URL
                urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+\.pdf', pdf_url)
                if urls:
                    return urls[0]
        
        return None
        
    except Exception as e:
        return None


def download_document(
    framework_name: str,
    document_url: str,
    download_dir: str,
    api_key: Optional[str] = None,
) -> Optional[str]:
    """Download framework document - uses robust logic from framework_testing.py"""
    import logging
    logger = logging.getLogger(__name__)
    
    if not document_url:
        logger.warning("No document_url provided for download")
        return None
    
    # Create download directory
    os.makedirs(download_dir, exist_ok=True)
    logger.info(f"Download directory: {download_dir}")
    
    def _attempt_download(url: str):
        logger.info(f"Downloading from: {url}")
        resp = requests.get(url, stream=True, timeout=60, allow_redirects=True)
        resp.raise_for_status()
        return resp
    
    try:
        url_to_fetch = document_url
        logger.info(f"Attempting to download from URL: {document_url}")
        
        # First, check if the URL is a direct PDF link
        if not document_url.lower().endswith('.pdf'):
            logger.info("URL does not end with .pdf, attempting to find direct PDF link...")
            if api_key:
                direct_pdf_url = find_actual_pdf_url(document_url, framework_name, api_key)
                if direct_pdf_url:
                    logger.info(f"Found direct PDF URL: {direct_pdf_url}")
                    url_to_fetch = direct_pdf_url
                else:
                    logger.warning("Could not find direct PDF URL, saving URL reference instead")
                    # Save the URL to a text file instead
                    safe_name = framework_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{safe_name}_{timestamp}_URL.txt"
                    filepath = os.path.join(download_dir, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(f"Framework: {framework_name}\n")
                        f.write(f"URL: {document_url}\n")
                        f.write(f"Note: This is a page URL, not a direct PDF link.\n")
                        f.write(f"Please visit the URL to download the document manually.\n")
                    
                    logger.info(f"Saved URL reference to: {filepath}")
                    return filepath
        
        # Try to download the file, with fallback if the direct link fails
        response = None
        try:
            response = _attempt_download(url_to_fetch)
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error downloading {url_to_fetch}: {http_err}")
            # If the direct link failed but we have an API key, ask Perplexity for another PDF URL
            if api_key:
                logger.info("Attempting to locate alternate PDF URL via Perplexity...")
                alternate_url = find_actual_pdf_url(document_url, framework_name, api_key)
                if alternate_url and alternate_url.lower().endswith('.pdf') and alternate_url != url_to_fetch:
                    logger.info(f"Alternate PDF URL found: {alternate_url}")
                    url_to_fetch = alternate_url
                    response = _attempt_download(url_to_fetch)
            if response is None:
                raise
        except Exception:
            raise
        
        # Check if we actually got a PDF
        content_type = response.headers.get('content-type', '').lower()
        logger.info(f"Response content-type: {content_type}")
        
        # Determine file extension
        if 'pdf' in content_type or url_to_fetch.lower().endswith('.pdf'):
            ext = '.pdf'
        elif 'zip' in content_type:
            ext = '.zip'
        elif 'excel' in content_type or 'spreadsheet' in content_type:
            ext = '.xlsx'
        elif 'word' in content_type or 'document' in content_type:
            ext = '.docx'
        elif 'html' in content_type:
            ext = '.html'
        else:
            ext = '.pdf'  # default
        
        logger.info(f"Detected file type: {ext}")
        
        # If we got HTML, save the URL instead
        if ext == '.html':
            logger.warning("Received HTML instead of document, saving URL reference")
            safe_name = framework_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_name}_{timestamp}_URL.txt"
            filepath = os.path.join(download_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Framework: {framework_name}\n")
                f.write(f"URL: {document_url}\n")
                f.write(f"Content-Type: {content_type}\n")
                f.write(f"Note: This URL returned HTML instead of a document.\n")
                f.write(f"Please visit the URL to download the document manually.\n")
            
            return filepath
        
        # Create filename
        safe_name = framework_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_{timestamp}{ext}"
        filepath = os.path.join(download_dir, filename)
        
        # Download file
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        logger.info(f"Downloading {total_size} bytes to: {filepath}")
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
        
        logger.info(f"Successfully downloaded {downloaded} bytes to: {filepath}")
        return filepath
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error downloading document: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None
    except Exception as e:
        logger.error(f"Unexpected error downloading document: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def run_framework_update_check(
    framework_name: str,
    last_updated_date: str,
    api_key: str,
    download_dir: Optional[str] = None,
    framework_id: Optional[int] = None,
    process_amendment: bool = False,
) -> dict:
    """
    Run the Perplexity check for a framework.

    Args:
        framework_name: Name of the framework
        last_updated_date: Last known update date (YYYY-MM-DD)
        api_key: Perplexity API key
        download_dir: Directory to save downloaded documents
        framework_id: Framework ID for processing (optional)
        process_amendment: Whether to process the downloaded amendment (default: False)

    Returns:
        dict with keys: has_update, latest_update_date, document_url, version,
        notes, downloaded_path (optional), processing_result (optional)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    download_folder = download_dir or "downloads"
    update_info = query_perplexity_api(framework_name, last_updated_date, api_key)

    downloaded_path = None
    processing_result = None
    
    # Log the update check results
    logger.info(f"Update check results for {framework_name}: has_update={update_info.get('has_update')}, document_url={update_info.get('document_url')}")
    
    if update_info.get("has_update") and update_info.get("document_url"):
        logger.info(f"Attempting to download document from: {update_info['document_url']}")
        try:
            downloaded_path = download_document(
                framework_name,
                update_info["document_url"],
                download_folder,
                api_key=api_key,
            )
            if downloaded_path:
                logger.info(f"Successfully downloaded amendment document for {framework_name} to {downloaded_path}")
                
                # Process the downloaded amendment if requested
                if process_amendment and framework_id and downloaded_path.lower().endswith('.pdf'):
                    try:
                        from .amendment_processor import process_downloaded_amendment
                        
                        logger.info(f"Starting amendment processing for {framework_name}")
                        
                        # Use the download directory as the output directory for processing
                        output_dir = download_dir if download_dir else os.path.dirname(downloaded_path)
                        
                        processing_result = process_downloaded_amendment(
                            pdf_path=downloaded_path,
                            framework_name=framework_name,
                            framework_id=framework_id,
                            amendment_date=update_info.get('latest_update_date', last_updated_date),
                            output_dir=output_dir
                        )
                        
                        if processing_result.get('success'):
                            logger.info(f"Successfully processed amendment: {processing_result.get('output_file')}")
                        else:
                            logger.error(f"Amendment processing failed: {processing_result.get('error')}")
                            
                    except Exception as e:
                        logger.error(f"Error processing amendment: {str(e)}")
                        import traceback
                        logger.error(traceback.format_exc())
                        processing_result = {
                            'success': False,
                            'error': str(e)
                        }
            else:
                logger.warning(f"Download failed or returned None for {framework_name}. document_url was: {update_info.get('document_url')}")
                        
        except Exception as e:
            logger.error(f"Error downloading document for {framework_name}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            downloaded_path = None
    else:
        if not update_info.get("has_update"):
            logger.info(f"No update found for {framework_name} (has_update=False)")
        elif not update_info.get("document_url"):
            logger.warning(f"Update found for {framework_name} but no document_url provided")

    result = {
        **update_info,
        "downloaded_path": downloaded_path,
    }
    
    if processing_result:
        result["processing_result"] = processing_result
    
    return result

