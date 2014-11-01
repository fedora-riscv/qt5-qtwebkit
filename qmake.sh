#!/bin/sh

qmake-qt5 \
  $@ \
  QMAKE_CFLAGS="${CFLAGS}" \
  QMAKE_CXXFLAGS="${CXXFLAGS}" \
  QMAKE_LFLAGS="${LDFLAGS}" \
