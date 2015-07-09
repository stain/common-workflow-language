#!/bin/sh

restore=0
if test -L cwltool/schemas ; then
  rm cwltool/schemas
  cp -r ../schemas cwltool/schemas
  restore=1
fi
docker build --file=cwltool_module.Dockerfile --tag=commonworkflowlanguage/cwltool_module .
docker build --file=cwltool_webapi.Dockerfile --tag=commonworkflowlanguage/cwltool_webapi .
docker build --file=cwltool.Dockerfile --tag=commonworkflowlanguage/cwltool .
if test $restore = 1 ; then
  rm -r cwltool/schemas
  ln -s ../../schemas cwltool/schemas
fi
