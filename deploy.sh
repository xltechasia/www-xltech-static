#!/bin/sh

# If a command fails then the deploy stops
set -e
GITROOT="$HOME/git/www-xltech-static"

cd $GITROOT

PUBLISH="NO"

case $1 in
  -h|-\?|--help)                  # Call a "show_help" function to display a synopsis, then exit.
    ##show_help
    exit
    ;;
  -p|--publish|-y|--yes|-l|--live)
    PUBLISH="YES"
    shift
    break
    ;;
  -np|--nopublish|--no-publish|-d|--draft|--no|-t|--test)
    PUBLISH="NO"
    shift
    break
    ;;
  *)
    PUBLISH="NO"
    shift
    break
    ;;
esac

case $PUBLISH in
  YES)
    printf "\t *** Publishing to Live Website\n"
    if [ -e no.publish ]; then
      rm no.publish
    fi
    touch yes.publish
    break
    ;;
  *)                              # Default case: If no more options then break out of the loop.
    printf "\t *** NOT Publishing to Live Website - Test/Draft Mode \n"
    if [ -e yes.publish ]; then
      rm yes.publish
    fi
    touch no.publish
    break
esac

printf "\033[0;32mDeploying updates to GitHub...\033[0m\n"

# Add changes to git.
git add .

# Commit changes.
msg="rebuilding site $(date)"
if [ -n "$*" ]; then
        msg="$msg - $*"
fi
git commit -m "$msg"

# Push source and build repos.
git push origin master

printf "\033[0;32mDeleting old public build files...\033[0m\n"

mkdir -p $GITROOT/public

if [ -d $GITROOT/public ]; then
  cd $GITROOT/public
  find -Esd . -not -iregex ".*\.git.*" -delete
  cd $GITROOT
fi

printf "\033[0;32mDeploying updates to GitHub Pages...\033[0m\n"

# Build the project.
hugo # if using a theme, replace with `hugo -t <YOURTHEME>`

# Go To Public folder
cd $GITROOT/public

case $PUBLISH in
  YES)
    printf "\t *** Publishing to Live Website\n"
    if [ -e no.publish ]; then
      rm no.publish
    fi
    touch yes.publish
    break
    ;;
  *)                              # Default case: If no more options then break out of the loop.
    printf "\t *** NOT Publishing to Live Website - Test/Draft Mode \n"
    if [ -e yes.publish ]; then
      rm yes.publish
    fi
    touch no.publish
    break
esac

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

cd $GITROOT

