OPTIONS = -N --highlight-style=tango --toc

all:
	pandoc ${OPTIONS} src/monads.md -o out/monads.pdf
	pandoc ${OPTIONS} src/monads.md -o out/monads.html
	pandoc ${OPTIONS} src/monads.md -o out/monads.docx
	pandoc ${OPTIONS} src/monads.md -o out/monads.epub
