# WideOrbit Song Logger

This project has three parts:

1. A WideOrbit Automation for Radio logging widget written in Java
2. A WideOrbit Automation for Radio discrepancy widget written in Java
3. Webapp backend API that takes queries from clients and works with a PostgreSQL database accordingly

## WideOrbit Logging Widget

The widget is an updated version of a currently existing WMTU project from 2015.

[Link to Project on GitHub](https://github.com/WMTU/woafr-song-log)

This version has updated libraries and slightly modified text in the UI, along with a reworking of how the widget connects to the backend to log songs.

View the README in the widget directory for more information.

## WideOrbit Discrepancy Widget

The widget is an updated version of a currently existing WMTU project from 2015.

[Link to Project on GitHub](https://github.com/WMTU/woafr-discrepancy-log)

This version has updated libraries and now submits using the API instead of writing directly to the database.

View the README in the widget directory for more information.

## Webapp

The webapp is a full rewrite of the WMTU legacy song logging API from 2015.

[Link to Project on GitHub](https://github.com/WMTU/Log)

The goal is to provide better operational support for current WMTU infrastructure along with better documentation for future development.

We also want to provide a web based interface to easily pull and check logs without needing to work with the database directly.

View the README in the webapp directory for more information.
