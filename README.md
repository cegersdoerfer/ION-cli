# ION CLI

A command-line utility for interacting with the ION web application. This tool allows you to upload trace files, manage analyses, and view results.

## Installation

```
bash
pip install ion-cli
```

## Features

- Upload trace files to the ION platform
- List your uploaded traces
- Launch analyses on your traces using different LLM models
- Stop running analyses
- View analysis results and diagnoses
- Delete traces and their associated files

## Usage

### Authentication

Before using the CLI, you need to authenticate with 
```
bash
ion-cli --user_email your.email@example.com
```

You can also set the `ION_USER_EMAIL` environment variable to avoid specifying your email with each command.

### Uploading a Trace

```
bash
ion-cli --upload path/to/your/trace.txt
```

### Listing Your Traces

```
bash
ion-cli --list
```

### Launching an Analysis

```
bash
ion-cli --analyze trace_name --llm anthropic/claude-3-7-sonnet-20250219
```

Available models:
- anthropic/claude-3-7-sonnet-20250219 (default)
- anthropic/claude-3-5-sonnet-20240620
- openai/gpt-4o
- openai/gpt-4o-mini


### Stopping an Analysis

```
bash
ion-cli --stop trace_name
```

### Viewing Analysis Results

Once an analysis is complete, you can view the diagnosis:

```
bash
ion-cli --view trace_name
```

### Deleting a Trace

```
bash
ion-cli --delete trace_name
```

## Command Reference

| Command | Alias | Description |
|---------|-------|-------------|
| `--upload`, `-u` | Path to the trace file to upload |
| `--user_email`, `-e` | Email address for authentication |
| `--list`, `-l` | List all your uploaded traces |
| `--analyze`, `-a` | Launch an analysis on the specified trace |
| `--stop`, `-s` | Stop a running analysis |
| `--view`, `-v` | View the diagnosis for a completed analysis |
| `--delete`, `-d` | Delete a trace and its associated files |
| `--llm`, `-m` | Specify the LLM model to use for analysis |

## Troubleshooting

If you encounter issues:

1. Ensure you're properly authenticated with a valid email
2. Check that your trace files are valid text files
3. For analyses that seem stuck, try using the `--stop` command and then restart

## License

[License information]