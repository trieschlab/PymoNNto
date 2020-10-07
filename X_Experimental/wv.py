
def mark_text(str, styles):#styles={"background-color:#FF0000":[text1,text2,...], }
    result = str
    for style, mark_str_list in styles.items():

        for mark_str in mark_str_list:
            result=result.replace(mark_str, '<a style="'+style+'";>'+mark_str+'</a>')

    return """<html>
    <head></head>
    <body>"""+result+"""</body>
    </html>"""

def show_html(str):

    f = open('temp.html', 'wb')
    f.write(str.encode())
    f.close()

    #import webbrowser
    #webbrowser.open_new_tab('temp.html')

    import webview
    webview.create_window('Hello world', 'temp.html')#
    webview.start()




html=mark_text('das ist ein test', {'background-color:#FF0000': ['das', 'ein'], 'color:#00FF00': ['test']})

show_html(html)

