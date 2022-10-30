# Rendermite
Rendermite is a tool used for dynamically generating item inventory icons for arbitrary versions of Minecraft.

# Usage
## Basic Usage
Show help message
```
python -m rendermite -h
```

Generate icons for the latest Minecraft **release**
```
python -m rendermite -v latest.release
```

Generate icons for the latest Minecraft **snapshot**
```
python -m rendermite -v latest.snapshot
```

Generate icons for an **arbitrary version** of Minecraft
```
python -m rendermite -v [version]
```
## Advanced Usage
Set output directory 
```
python -m rendermite -v [version] -o ./output
```

Set temporary directory for Minecraft assets to be extracted into
```
python -m rendermite -v [version] -t /tmp/rendermite
```

Set max child processes to allow multiprocessessing. Values < 2 will run in a single process.
```
python -m rendermite -v [version] -p 5
```