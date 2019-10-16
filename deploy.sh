#!/bin/sh

# If a command fails then the deploy stops
set -e

cd ~/git/www-xltech-static

case $1 in
  -h|-\?|--help)                  # Call a "show_help" function to display a synopsis, then exit.
    ##show_help
    exit
    ;;
  -p|--publish|-y|--yes*)
    echo -e "\t *** Publishing to Live Website\n"
    rm no.publish
    touch yes.publish
    shift
    break
    ;;
  -np|--nopublish|--no-publish|-d|--draft|--no|-t|--test)
    shift
    ;;
  *)                              # Default case: If no more options then break out of the loop.
    echo -e "\t *** NOT Publishing to Live Website - Test/Draft Mode \n"
    rm yes.publish
    touch no.publish
    break
esac

printf "\033[0;32mDeploying updates to GitHub...\033[0m\n"

# Add changes to git.
git add .

# Commit changes.
msg="rebuilding site $(date)"
if [ -n "$*" ]; then
        msg="$*"
fi
git commit -m "$msg"

# Push source and build repos.
git push origin master

printf "\033[0;32mDeploying updates to GitHub Pages...\033[0m\n"

# Build the project.
hugo # if using a theme, replace with `hugo -t <YOURTHEME>`

# Go To Public folder
cd public

# Add changes to git.
git add .

# Commit changes.
msg="rebuilding site $(date)"
if [ -n "$*" ]; then
	msg="$*"
fi
git commit -m "$msg"

# Push source and build repos.
git push origin master

cd ..

