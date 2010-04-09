"""Substitute chapters -> sections, sections -> subsections, etc..."""

import re

def manual2article(text):
    text = re.sub(r"\\subsubsection\*?", r"\\paragraph\*", text)
    text = re.sub(r"\\subsection\*?", r"\\subsubsection\*", text)
    text = re.sub(r"\\section\*?", r"\\subsection", text)
    text = re.sub("section ","Section~",text)
    text = re.sub("Section ","Section~",text)
    text = re.sub(r"\\chapter", r"\\section", text)
    text = re.sub("chapter ","Section~",text)    
    text = re.sub("Chapter ","Section~",text)
    text = re.sub(" chapter", " section",text)
    for code_alias in ['module','texttt','function','file','class']:
        text = re.sub(r"\\%s{"%code_alias, "\code{", text)
    text = re.sub(r'^T',r'\\top',text)
    
    # Dedent all code blocks
    re.DOTALL=True
    codeblock = re.compile(r'\\begin{verbatim}[^&]*\\end{verbatim}')
    codeblocks = codeblock.findall(text)
    for match in codeblocks:
        if match.count(r'\\begin')>0:
            continue
        text = text.replace(match, match.replace('\n\t','\nTAB').replace('\n    ','\nTAB').replace('\n   ','\nTAB').replace('TAB',''))
    
    # Destroy all boxes
    boxblock = re.compile(r'\\fbox{[^#]*}')
    boxblocks = boxblock.findall(text)
    for match in boxblocks:
        text = text.replace(match, '')
    
    # Convert verbatim blocks to CodeInput blocks
    text = re.sub(r'\\begin{verbatim}',r'\\begin{CodeInput}',text)
    text = re.sub(r'\\end{verbatim}',r'\\end{CodeInput}',text)
    
    #text = re.sub(r"\\hypertarget\{.*", r"", text)
    text = re.sub(r"\\pdfbookmark.*", r"", text)
    for pkgname in ['PyMC','NumPy','SciPy','PyTables','Matplotlib','Pylab','Pyrex']:
        text = re.sub(pkgname, r'\\pkg{%s}'%pkgname,text)
    for proglang in ['Python','Fortran']:
        text = re.sub(proglang, r'\\proglang{%s}'%proglang, text)
    return text

if __name__ == '__main__':
    import sys
    f = open(sys.argv[1], 'r')
    text = f.read()
    print manual2article(text)
