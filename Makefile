OPTIONS = -N --highlight-style=tango --toc

all:
	pandoc ${OPTIONS} monads.md -o monads.pdf
	pandoc ${OPTIONS} monads.md -o monads.html
	pandoc ${OPTIONS} monads.md -o monads.docx
	pandoc ${OPTIONS} monads.md -o monads.epub
