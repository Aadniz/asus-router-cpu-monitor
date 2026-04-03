# Asus Router CPU Monitor

Monitor your ASUS router's CPU cores from the terminal!

Inspired by prettyping, easier to visualize if the CPUs are overloaded.

![asus-system-status-panel](/docs/screenshots/asus_router.png "Asus system status panel") ![asus-cpu-monitor-in-the-terminal](/docs/screenshots/asus_terminal.png "Asus CPU monitor in the terminal")

## How it works

It communicates with Asus's web dashboard under the hood, calling .asp and .cgi routes.
Maybe a more elegant solution could be to communicate with the router over SSH instead.

## Known issues

### Multiple sessions

As it is now, you cannot be signed into the web dashboard at the same time as you're running this cli tool.
