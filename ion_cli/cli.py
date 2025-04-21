#!/usr/bin/env python
"""
Command line utility for uploading .txt files to a public endpoint.
"""

import argparse
import os
import sys
import requests
import subprocess
from typing import Optional
from ion_cli.config import DEFAULT_API_ENDPOINT, SUPPORTED_MODELS, VALID_TASK_STATUSES, VALID_STATUS_FOR_VIEW

# Import Rich components
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.theme import Theme
from rich.traceback import install

# Install rich traceback handler for better error display
install()


# Create a custom theme
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
})

# Create console with custom theme
console = Console(theme=custom_theme)


def validate_file(file_path: str) -> bool:
    """
    Validate that the file exists and is a .txt file.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        bool: True if file is valid, False otherwise
    """
    if not os.path.exists(file_path):
        console.print(f"[error]Error:[/] File '{file_path}' does not exist.")
        return False
    
    # Try to detect if the file is actually text
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Try to read a small sample of the file
            sample = file.read(1024)
            
            # Check if the sample contains null bytes, which typically indicate binary data
            if '\0' in sample:
                console.print(f"[error]Error:[/] File '{file_path}' appears to be a binary file, not a text file.")
                return False
                
    except UnicodeDecodeError:
        console.print(f"[error]Error:[/] File '{file_path}' contains invalid text encoding.")
        return False
    except Exception as e:
        console.print(f"[error]Error reading file:[/] '{file_path}': {str(e)}")
        return False
    
    return True


def validate_email(email: str) -> bool:
    """
    Simple validation for email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email format is valid, False otherwise
    """
    if '@' not in email or '.' not in email:
        console.print(f"[error]Error:[/] '{email}' does not appear to be a valid email address.")
        return False
    
    return True


def upload_file(file_path: str, user_id: str) -> bool:
    """
    Upload the file to the public endpoint.
    
    Args:
        file_path: Path to the file to upload
        user_id: User's ID
        
    Returns:
        bool: True if upload was successful, False otherwise
    """
    
    try:
        # Open the file in binary mode
        with open(file_path, 'rb') as file:
            # Create a multipart form-data request
            files = {
                'file': (os.path.basename(file_path), file, 'text/plain')
            }
            
            form_data = {
                'user_id': user_id
            }
            
            # Show a spinner during upload
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("[info]Uploading file...[/]", total=None)
                response = requests.post(
                    f"{DEFAULT_API_ENDPOINT}/api/upload_trace", 
                    files=files,
                    data=form_data
                )
                progress.update(task, completed=True)

        if response.status_code == 400 and "already exists" in response.text:
            console.print(Panel(f"[warning]File '{os.path.basename(file_path)}' already exists.[/]", 
                                title="Warning", border_style="yellow"))
            return True
        
        if response.status_code == 200:
            console.print(Panel(f"[success]File '{os.path.basename(file_path)}' successfully uploaded.[/]", 
                               title="Success", border_style="green"))
            return True
        else:
            console.print(Panel(f"[error]Error uploading file:[/] {response.text}", 
                               title="Error", border_style="red"))
            return False
            
    except Exception as e:
        console.print(Panel(f"[error]Error uploading file:[/] {str(e)}", 
                           title="Error", border_style="red"))
        return False
    

def list_user_traces(user_id: str) -> bool:
    """
    List all traces uploaded by the user.
    
    Args:
        user_id: User's ID
        
    Returns:
        bool: True if listing was successful, False otherwise
    """
    try:
        # Prepare the request payload
        payload = {
            'user_id': user_id
        }
        
        # Show a spinner during the request
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[info]Fetching your traces...[/]", total=None)
            response = requests.post(f"{DEFAULT_API_ENDPOINT}/api/user_traces", json=payload)
            progress.update(task, completed=True)
        
        if response.status_code == 200:
            traces = response.json()
            
            if not traces:
                console.print("[info]You haven't uploaded any traces yet.[/]")
                return True
            
            # Create a table to display the traces
            from rich.table import Table
            table = Table(title="Your Uploaded Traces")
            
            # Add columns
            table.add_column("Trace Name", style="cyan")
            table.add_column("Description", style="green")
            table.add_column("Upload Date", style="yellow")
            table.add_column("Status", style="magenta")
            table.add_column("Model", style="blue")
            
            # Add rows
            for trace in traces:
                status_style = {
                    "completed": "[green]Completed[/]",
                    "in_progress": "[yellow]In Progress[/]",
                    "not_started": "[grey]Not Started[/]",
                    "failed": "[red]Failed[/]"
                }.get(trace.get('status', 'not_started'), trace.get('status', 'not_started'))
                
                table.add_row(
                    trace.get('trace_name', 'Unknown'),
                    trace.get('trace_description', 'No description'),
                    trace.get('upload_date', 'Unknown'),
                    status_style,
                    trace.get('model', 'gpt-4o')
                )
            
            # Print the table
            console.print(table)
            return True
        else:
            error_msg = response.json().get('error', 'Unknown error')
            console.print(Panel(f"[error]Error listing traces:[/] {error_msg}", 
                               title="Error", border_style="red"))
            return False
            
    except Exception as e:
        console.print(Panel(f"[error]Error listing traces:[/] {str(e)}", 
                           title="Error", border_style="red"))
        return False


def check_user_verified(user_email: str = None) -> str:
    """
    Check if the user is verified.
    If user_email is not provided, check environment variable ION_USER_EMAIL.
    """
    if not user_email:
        user_email = os.environ.get("ION_USER_EMAIL")
        if not user_email:
            console.print(Panel(
                "[error]User email not provided and ION_USER_EMAIL environment variable not set.[/]\n"
                "Please run [bold]ION-upload --user_email <email>[/] or set the ION_USER_EMAIL environment variable.",
                title="Authentication Error",
                border_style="red"
            ))
            return None
        if not validate_email(user_email):
            return None
        else:
            console.print(f"[info]Using user email from environment:[/] {user_email}")
    else:
        # set the env variable
        os.environ["ION_USER_EMAIL"] = user_email
        console.print(f"[info]Setting user email environment variable:[/] {user_email}")

    request_body = {
        "email": user_email
    }
    
    # Show a spinner during verification
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[info]Verifying user...[/]", total=None)
        response = requests.post(f"{DEFAULT_API_ENDPOINT}/api/user", json=request_body)
        progress.update(task, completed=True)
    
    result = response.json()
    user_id = result.get("user_id")

    if user_id:
        console.print(f"[success]User verified:[/] {user_email}")
    else:
        console.print(Panel(
            f"[warning]User not verified:[/] {user_email}\n"
            "Please check your email for verification instructions.",
            title="Verification Required",
            border_style="yellow"
        ))
        return None
    
    return user_id




def get_trace_status(trace_name: str, user_id: str) -> str:
    """
    Get the status of a specific trace.
    """
    payload = {
        "user_id": user_id
    }
    response = requests.post(f"{DEFAULT_API_ENDPOINT}/api/user_traces", json=payload)
    traces = response.json()
    for trace in traces:
        if trace["trace_name"] == trace_name:
            return trace["status"]
    return None

def check_trace_name_valid(trace_name: str, user_id: str) -> bool:
    """
    Uses the user_traces endpoint to check if a trace name is in the user's traces
    """
    status = get_trace_status(trace_name, user_id)
    if status is None:
        console.print(Panel(
            f"[error]Error:[/] Trace '{trace_name}' not found.",
            title="Error",
            border_style="red"
        ))
        return False
    if status in VALID_TASK_STATUSES:
        return True
    else:
        console.print(Panel(
            f"[error]Error:[/] Trace '{trace_name}' is currently {status}, please wait for it to complete or delete it.",
            title="Error",
            border_style="red"
        ))
        return False


def launch_analysis(trace_id: str, user_id: str, llm: str) -> bool:
    """
    Launch an analysis for a specific trace.
    
    Args:
        trace_id: ID or name of the trace to analyze
        user_id: User's ID
        llm: Language model to use for analysis
        
    Returns:
        bool: True if analysis was successfully launched, False otherwise
    """
    try:
        if not check_trace_name_valid(trace_id, user_id):
            console.print(Panel(
                f"[error]Error:[/] Trace '{trace_id}' not found.",
                title="Error",
                border_style="red"
            ))
            return False
        # Prepare the request payload
        payload = {
            'user_id': user_id,
            'trace_name': trace_id,
            'llm': llm
        }
        
        # Show a spinner during the request
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[info]Launching analysis...[/]", total=None)
            response = requests.post(f"{DEFAULT_API_ENDPOINT}/api/run_analysis", json=payload)
            progress.update(task, completed=True)
        
        if response.status_code == 202:
            result = response.json()
            task_id = result.get('task_id')
            console.print(Panel(
                f"[success]Analysis task submitted successfully![/]\n"
                f"Task ID: {task_id}\n"
                f"Trace: {trace_id}\n"
                f"Model: {llm}",
                title="Analysis Launched",
                border_style="green"
            ))
            return True
        else:
            error_msg = response.json().get('error', 'Unknown error')
            console.print(Panel(
                f"[error]Error launching analysis:[/] {error_msg}",
                title="Error",
                border_style="red"
            ))
            return False
            
    except Exception as e:
        console.print(Panel(
            f"[error]Error launching analysis:[/] {str(e)}",
            title="Error",
            border_style="red"
        ))
        return False
    

def view_trace_diagnosis(trace_name: str, user_id: str) -> bool:
    """
    View the final diagnosis for a specific trace.
    
    Args:
        trace_name: Name of the trace to view diagnosis for
        user_id: User's ID
        
    Returns:
        bool: True if viewing was successful, False otherwise
    """
    try:
        # First check if the trace status is valid for viewing
        status = get_trace_status(trace_name, user_id)
        if status not in VALID_STATUS_FOR_VIEW:
            console.print(Panel(
                f"[error]Error:[/] Trace '{trace_name}' is not ready for viewing. Current status: {status}",
                title="Error",
                border_style="red"
            ))
            return False
        
        # Prepare the request payload
        payload = {
            'user_id': user_id
        }
        
        # Show a spinner during the request
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[info]Fetching diagnosis...[/]", total=None)
            response = requests.post(f"{DEFAULT_API_ENDPOINT}/api/trace_examples/{trace_name}/final_diagnosis", json=payload)
            progress.update(task, completed=True)
        
        if response.status_code == 200:
            result = response.json()
            diagnosis = result.get('trace_diagnosis', {})
            content = diagnosis.get('content', 'No diagnosis content available')
            sources = diagnosis.get('sources', [])
            
            # Display the diagnosis content
            from rich.markdown import Markdown
            console.print(Panel(
                Markdown(content),
                title=f"Diagnosis for {trace_name}",
                border_style="green",
                expand=False
            ))
            
            # Display sources if available
            if sources:
                from rich.table import Table
                from rich.markdown import Markdown
                source_table = Table(title="Sources", show_lines=True)
                source_table.add_column("Source File", style="cyan")
                source_table.add_column("Excerpts", style="green")
                
                for source in sources:
                    file_name = source.get('file', 'N/A')
                    excerpts = source.get('text', [])
                    
                    # Join multiple excerpts with newlines
                    if isinstance(excerpts, list):
                        excerpt_text = "\n\n".join(excerpts)
                    else:
                        excerpt_text = str(excerpts)
                    
                    # Render markdown in the excerpts
                    source_table.add_row(file_name, Markdown(excerpt_text))
                
                console.print(source_table)
            
            return True
        elif response.status_code == 404:
            console.print(Panel(
                f"[warning]Diagnosis not found for trace '{trace_name}'.[/]",
                title="Not Found",
                border_style="yellow"
            ))
            return False
        else:
            error_msg = response.json().get('error', 'Unknown error')
            console.print(Panel(
                f"[error]Error fetching diagnosis:[/] {error_msg}",
                title="Error",
                border_style="red"
            ))
            return False
            
    except Exception as e:
        console.print(Panel(
            f"[error]Error viewing diagnosis:[/] {str(e)}",
            title="Error",
            border_style="red"
        ))
        return False

def stop_analysis(trace_name: str, user_id: str) -> bool:
    """
    Stop an analysis for a specific trace.
    
    Args:
        trace_name: Name of the trace to stop analysis for
        user_id: User's ID
        
    Returns:
        bool: True if stopping was successful, False otherwise
    """
    try:
        # Prepare the request payload
        payload = {
            'user_id': user_id,
            'trace_name': trace_name
        }
        
        # Show a spinner during the request
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[info]Stopping analysis...[/]", total=None)
            response = requests.post(f"{DEFAULT_API_ENDPOINT}/api/stop_analysis", json=payload)
            progress.update(task, completed=True)
        
        if response.status_code == 200:
            console.print(Panel(
                f"[success]Analysis for trace '{trace_name}' successfully stopped.[/]",
                title="Success",
                border_style="green"
            ))
            return True
        else:
            error_msg = response.json().get('error', 'Unknown error')
            console.print(Panel(
                f"[error]Error stopping analysis:[/] {error_msg}",
                title="Error",
                border_style="red"
            ))
            return False
            
    except Exception as e:
        console.print(Panel(
            f"[error]Error stopping analysis:[/] {str(e)}",
            title="Error",
            border_style="red"
        ))
        return False

def delete_trace(trace_name: str, user_id: str) -> bool:
    """
    Delete a specific trace and all its associated files.
    
    Args:
        trace_name: Name of the trace to delete
        user_id: User's ID
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        trace_status = get_trace_status(trace_name, user_id)
        if trace_status not in VALID_TASK_STATUSES:
            stop_result = stop_analysis(trace_name, user_id)
            if not stop_result:
                console.print(Panel(
                    f"[error]Error stopping analysis:[/] {str(e)}",
                    title="Error",
                    border_style="red"
                ))
                # ask if it should be retried
                confirmation = input("Do you want to retry stopping the analysis? (y/N): ").lower()
                if confirmation == 'y':
                    return delete_trace(trace_name, user_id)
                else:
                    console.print("[info]Deletion cancelled.[/]")
                    return False
            
        # Confirm deletion
        console.print(f"[warning]Warning:[/] You are about to delete trace '{trace_name}'.")
        confirmation = input("Are you sure you want to proceed? (y/N): ").lower()
        
        if confirmation != 'y':
            console.print("[info]Deletion cancelled.[/]")
            return False
        
        # Prepare the request payload
        payload = {
            'user_id': user_id,
            'trace_name': trace_name
        }
        
        # Show a spinner during the request
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[info]Deleting trace...[/]", total=None)
            response = requests.post(f"{DEFAULT_API_ENDPOINT}/api/delete_trace", json=payload)
            progress.update(task, completed=True)
        
        if response.status_code == 200:
            console.print(Panel(
                f"[success]Trace '{trace_name}' successfully deleted.[/]",
                title="Success",
                border_style="green"
            ))
            return True
        else:
            error_msg = response.json().get('error', 'Unknown error')
            console.print(Panel(
                f"[error]Error deleting trace:[/] {error_msg}",
                title="Error",
                border_style="red"
            ))
            return False
            
    except Exception as e:
        console.print(Panel(
            f"[error]Error deleting trace:[/] {str(e)}",
            title="Error",
            border_style="red"
        ))
        return False

def main(args: Optional[list] = None) -> int:
    """
    Main entry point for the command line utility.
    
    Args:
        args: Command line arguments (used for testing)
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    # Print a welcome banner
    console.print(Panel.fit(
        "[bold cyan]ION-cli[/bold cyan] - The I/O Navigator CLI",
        border_style="cyan"
    ))
    
    parser = argparse.ArgumentParser(
        description="The I/O Navigator CLI"
    )
    
    parser.add_argument(
        "--upload", "-u",
        type=str,
        required=False,
        help="Path to the .txt file to upload"
    )
    
    parser.add_argument(
        "--user_email", "-e",
        type=str,
        required=False,
        help="Email address of the user"
    )

    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all files uploaded by the user"
    )

    parser.add_argument(
        "--analyze", "-a",
        type=str,
        required=False,
        help="Launch a trace analysis"
    )

    parser.add_argument(
        "--stop", "-s",
        type=str,
        required=False,
        help="Stop a running trace analysis"
    )

    parser.add_argument(
        "--delete", "-d",
        type=str,
        required=False,
        help="Delete a specific trace"
    )

    parser.add_argument(
        "--llm", "-m",
        type=str,
        choices=SUPPORTED_MODELS,
        default="anthropic/claude-3-7-sonnet-20250219",
        help="Specify the LLM to use for analysis"
    )

    parser.add_argument(
        "--view", "-v",
        type=str,
        required=False,
        help="View the final diagnosis for a specific trace"
    )
    
    parsed_args = parser.parse_args(args)
    
    user_id = check_user_verified(parsed_args.user_email)
    if not user_id:
        return 1

    if parsed_args.upload:
        if not validate_file(parsed_args.upload):
            return 1
        
        success = upload_file(parsed_args.upload, user_id)
        return 0 if success else 1
    
    # If no file is specified but --list is used, list the user's files
    if parsed_args.list:
        success = list_user_traces(user_id)
        return 0 if success else 1
    
    if parsed_args.analyze:
        success = launch_analysis(parsed_args.analyze, user_id, parsed_args.llm)
        return 0 if success else 1
    
    if parsed_args.stop:
        success = stop_analysis(parsed_args.stop, user_id)
        return 0 if success else 1
        
    if parsed_args.delete:
        success = delete_trace(parsed_args.delete, user_id)
        return 0 if success else 1
    
    if parsed_args.view:
        success = view_trace_diagnosis(parsed_args.view, user_id)
        return 0 if success else 1
        
    # If no action is specified, show help
    if not (parsed_args.upload or parsed_args.list or parsed_args.analyze or parsed_args.stop or parsed_args.delete or parsed_args.view):
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 