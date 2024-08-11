


def check_status(response):
    status = response.status_code
    if status == 200:
        return True
    elif status == 404:
        print(">>>>>>> page not found for url",response.url)
        return False
    else:
        print(f">>>>>>>>>>>> invalid status found:{status} for url:{response.url}")
        return False


def check_content_type(response):
    content_type = response.headers.get('Content-Type', '')
    # Check the Content-Type
    start_bytes = response.content[:5]
    if 'application/pdf' in content_type or start_bytes.startswith(b'%PDF-'):
        # print(f"The content is a PDF. for url{response.url}")
        return 'PDF'
    elif 'text/html' in content_type :
        # print(f"The content is HTML. for url{response.url}")
        return 'HTML'
    else:
        print(f"Unknown content type : {content_type} for url: {response.url}")
        return content_type