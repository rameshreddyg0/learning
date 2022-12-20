from tabulate import tabulate

def print_error(message):
  print("\033[31m %s \033[0m" %(message))
 
def print_warning(message):
  print("\033[33m %s \033[0m" %(message))
  
def print_success(message):
  print("\033[32m %s \033[0m" %(message))
  
def print_notification(message):
  print("\033[34m %s \033[0m" %(message))

def tabulate_content(headers, dataForTable, isSuccess):
  if isSuccess:
    print_success(tabulate(dataForTable, headers, tablefmt="pretty"))
  else:
    print_error(tabulate(dataForTable, headers, tablefmt="pretty"))

def set_api_token(session, api_token):
  session.headers.update({'Authorization': 'Bearer {api_token}'.format(api_token = api_token)})

def set_content_type(session, content_type):
  session.headers.update({'Content-Type': '{content_type}'.format(content_type = content_type)})

def construct_html_success(heading, stdout_body):
  debug_diagnostics_heading = heading if stdout_body else "NO CONTENT FOUND TO BE LOGGED"
  return """<html>
          <head><h1>{html_heading}</h1></head>
          <body><font color = "green"><p><pre>{html_body}</pre></p></font></body>
          </html>""".format(html_heading = debug_diagnostics_heading, html_body = stdout_body)

def construct_html_error(heading, stdout_body, stderror_body):
  debug_diagnostics_heading = "Debug Diagnostic" if stdout_body else ""
  error_diagnostics_heading = "Error Diagnostic" if stderror_body else ""
  if debug_diagnostics_heading == "" and error_diagnostics_heading == "":
    heading = "NO CONTENT FOUND TO BE LOGGED"
  return """<html>
            <head><h1>{html_heading}</h1></head>
            <body><p>{debug_diagnostics}</p> \n \
              <font color = "red"><p><pre>{html_stdout_body}</pre></p></font>\n \
              <p>{error_diagnostics}</p> \n \
              <font color = "red"><p><pre>{html_stderror_body}</pre></p></font></body>
            </html>""".format(html_heading = heading, debug_diagnostics = debug_diagnostics_heading, html_stdout_body = stdout_body, error_diagnostics = error_diagnostics_heading, html_stderror_body = stderror_body) 

def construct_html_message_success(message):
  return """<html>
          <body><font color = "green"><p><pre>{html_body}</pre></p></font></body>
          </html>""".format(html_body = message)

def construct_html_message_error(message):
      return """<html>
          <body><font color = "red"><p><pre>{html_body}</pre></p></font></body>
          </html>""".format(html_body = message)

def getDockerContainerCmd(mounting_workspace, container):
  return ('docker container run --rm ' + mounting_workspace + ' ' + container + ' ')
