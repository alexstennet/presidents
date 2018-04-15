## env: creates anaconda environment with all the correct packages required to recreate the original's results
.PHONY : env
env : 
	conda env create -f environment.yml

## help: displays what each make command does
.PHONY : help
help : Makefile
	@sed -n 's/^##//p' $<