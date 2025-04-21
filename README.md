# ION CLI

A command-line utility for interacting with the ION web application. This tool allows you to upload trace files, manage analyses, and view results.

## Installation

```bash
git clone https://github.com/cegersdoerfer/ION-cli.git
cd ION-cli
pip install -e .
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

Option 1: add your email as an arg for each command
```bash
ion-cli [--user_email, -e] your.email@example.com [other args]
```

Option 2: Set the `ION_USER_EMAIL` environment variable to avoid specifying your email with each command:

```bash
export ION_USER_EMAIL=test@example.com
```

### Uploading a Trace

Upload trace files in txt (output of `darshan-parser`) or Darshan log format.

```bash
ion-cli --upload path/to/your/trace.[txt, darshan]
```

### List Uploaded Traces

```bash
ion-cli --list
```
```txt               
╭─────────────────────────────────╮
│ ION-cli - The I/O Navigator CLI │
╰─────────────────────────────────╯
Using user email from environment: test@example.com
⠙ Verifying user...
User verified: test@example.com
⠙ Fetching your traces...
                               Your Uploaded Traces                               
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Trace Name  ┃ Description         ┃ Upload Date         ┃ Status      ┃ Model  ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━┩
│ valid_trace │ User uploaded trace │ 2025-03-02 12:51:44 │ Not Started │ gpt-4o │
└─────────────┴─────────────────────┴─────────────────────┴─────────────┴────────┘
```

### Launch an Analysis

```bash
ion-cli --analyze trace_name --llm anthropic/claude-3-7-sonnet-20250219
```
```txt
⠋ Launching analysis...
╭─────────────────────────────────────────────────────────── Analysis Launched ───────────────────────────────────────────────────────────╮
│ Analysis task submitted successfully!                                                                                                   │
│ Task ID: 7894f946-bbd4-469f-93a2-2c832c772fb6                                                                                           │
│ Trace: valid_trace                                                                                                                      │
│ Model: anthropic/claude-3-7-sonnet-20250219                                                                                             │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Available models:
- anthropic/claude-3-7-sonnet-20250219 (default)
- anthropic/claude-3-5-sonnet-20240620
- openai/gpt-4o
- openai/gpt-4o-mini
- openai/gpt-4.1
- openai/gpt-4.1-mini


### Stopping an Analysis

```bash
ion-cli --stop trace_name
```

### Viewing Analysis Results

Once an analysis is complete, you can view the diagnosis:

```bash
ion-cli --view trace_name
```
```txt

⠴ Fetching diagnosis...
╭─────────────────────────────────────────────────────── Diagnosis for valid_trace ───────────────────────────────────────────────────────╮
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │
│ ┃                          HPC I/O Performance Diagnosis: Inefficient Configuration and Resource Utilization                          ┃ │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │
│                                                                                                                                         │
│                                                                                                                                         │
│                                                          Application Overview                                                           │
│                                                                                                                                         │
│  • Runtime: 722 seconds with 8 processes                                                                                                │
│  • Write-dominated workload: 920 MB written versus only 58.4 KB read                                                                    │
│  • I/O breakdown: POSIX (99.82%), MPI-IO (0.18%), STDIO (minimal, only 777 bytes)                                                       │
│                                                                                                                                         │
│                                                                                                                                         │
│                                                       Critical Performance Issues                                                       │
│                                                                                                                                         │
│                                                 Limited Lustre File System Parallelism                                                  │
│                                                                                                                                         │
│  • Suboptimal striping configuration: All 11 files use a stripe width of 1 (single OST per file)                                        │
│  • Significant under-utilization: Only 11 of 274 available OSTs used (4% utilization)                                                   │
│  • Default stripe size of 1MB: Not optimized for application's I/O pattern                                                              │
│  • One-to-one mapping pattern: Each file is accessed by exactly one rank and stored on one OST                                          │
│                                                                                                                                         │
│                                               Inefficient I/O Operations and Distribution                                               │
│                                                                                                                                         │
│  • Dominance of small MPI-IO operations: Approximately 89% of all MPI-IO operations are under 1KB                                       │
│     • 63% are very small (0-100 bytes)                                                                                                  │
│     • 26% are between 100-1KB                                                                                                           │
│  • Large POSIX operations: 99.97% of POSIX write operations are in the 100KB-1MB range                                                  │
│  • Load imbalance: Despite having 8 processes, only 2 ranks perform POSIX operations to shared files                                    │
│  • Custom aggregation: Application performs its own data aggregation rather than using MPI-IO's collective buffering                    │
│                                                                                                                                         │
│                                                     Suboptimal Collective I/O Usage                                                     │
│                                                                                                                                         │
│  • Mixed collective approach: Collective writes used (61.5% of MPI-IO operations) but no collective reads                               │
│  • Minimal MPI-IO utilization: Only 0.18% of total I/O volume uses MPI-IO                                                               │
│  • Absence of non-blocking I/O: No asynchronous I/O despite being a write-intensive workload                                            │
│  • High metadata to data ratio: 48 file view operations vs 27 data operations per file                                                  │
│                                                                                                                                         │
│                                                        HDF5 File Access Pattern                                                         │
│                                                                                                                                         │
│  • Access to multiple HDF5 files (plt0000X.h5) with identical patterns                                                                  │
│  • Consistent small access sizes (512, 544, and 272 bytes) across files                                                                 │
│                                                                                                                                         │
│                                                                                                                                         │
│                                                          Performance Strengths                                                          │
│                                                                                                                                         │
│                                                       Well-Optimized Data Access                                                        │
│                                                                                                                                         │
│  • Sequential access: 99.9% of POSIX writes are sequential                                                                              │
│  • Consecutive access: 99.98% of POSIX writes are consecutive                                                                           │
│  • Excellent alignment: Over 99.996% of all I/O operations are properly aligned to 1MB boundaries                                       │
│  • Efficient interface selection: Appropriate use of POSIX for bulk data and STDIO only for minimal logging                             │
│  • Low read/write switching: Only 20 read/write switches observed, indicating effective separation of phases                            │
│                                                                                                                                         │
│                                                        Minimal Metadata Overhead                                                        │
│                                                                                                                                         │
│  • Low metadata operation time: Only 0.293 seconds (0.04% of execution time)                                                            │
│  • Average metadata latency: 0.7 milliseconds per operation                                                                             │
│                                                                                                                                         │
│                                                                                                                                         │
│                                                      Performance Impact Assessment                                                      │
│                                                                                                                                         │
│                                                         Bottlenecked Bandwidth                                                          │
│                                                                                                                                         │
│ By restricting I/O to only 11 OSTs with a stripe count of 1, the application cannot benefit from the full bandwidth of the Lustre file  │
│ system. Each file's I/O operations are directed to a single storage target, creating performance bottlenecks.                           │
│                                                                                                                                         │
│                                                      Latency-Dominated Performance                                                      │
│                                                                                                                                         │
│ The dominance of small MPI-IO operations leads to inefficient resource utilization, with latency costs overshadowing actual data        │
│ transfer time. Studies show proper Lustre configurations can improve performance by up to two-fold compared to poor configurations.     │
│                                                                                                                                         │
│                                                     Missed Parallelism Opportunity                                                      │
│                                                                                                                                         │
│ In Lustre file systems, large files are typically striped across multiple OSTs to achieve high throughput through parallel I/O          │
│ operations. The current configuration fails to exploit this fundamental feature of Lustre architecture.                                 │
│                                                                                                                                         │
│                                                     Custom Aggregation Limitations                                                      │
│                                                                                                                                         │
│ While the application performs its own data aggregation (evidenced by few ranks writing large volumes), this approach misses            │
│ optimizations that MPI-IO collective operations could provide, such as better coordination with the filesystem and potential for        │
│ asynchronous operations.                                                                                                                │
│                                                                                                                                         │
│                                                        Current Scale Assessment                                                         │
│                                                                                                                                         │
│ At the current small scale (8 processes), these issues are not causing severe performance problems:                                     │
│                                                                                                                                         │
│  • Metadata time is very low (0.04% of execution time)                                                                                  │
│  • Uniform I/O distribution across ranks suggests well-balanced operations                                                              │
│  • Sequential and aligned operations demonstrate good access patterns                                                                   │
│                                                                                                                                         │
│ However, these issues would likely become significant performance bottlenecks if the application were to scale to larger process        │
│ counts. The limited Lustre striping, custom aggregation approach, and minimal use of MPI-IO collective functionality would increasingly │
│ restrict performance at scale.                                                                                                          │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
                                                                  Sources                                                                  
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Source File                                                        ┃ Excerpts                                                           ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ comprehensive-measurement-and-analysis-of-the-user-perceived-i-o-… │ V. MEASUREMENT RESULTS AND ANALYSIS                                │
│                                                                    │                                                                    │
│                                                                    │ In Lustre file system, the large files are usually striped and     │
│                                                                    │ stored on different OSTs across the system to achieve high         │
│                                                                    │ throughput. Those data chunks are bulk transferred between the     │
│                                                                    │ Lustre clients and the OSTs through a large-scale and highspeed    │
│                                                                    │ network. In this section, we present and analyze the measurement   │
│                                                                    │ results of the user-perceived I/O performance under two scenarios  │
├────────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
│ dca-io-a-dynamic-i-o-control-scheme-for-parallel-and-distributed-… │ A. Lustre file system                                              │
│                                                                    │                                                                    │
│                                                                    │ Lustre file system [4] is a parallel and distributed file system   │
│                                                                    │ which is used in many HPC environments including CORI. Figure 1    │
│                                                                    │ shows overall architecture of Lustre file system. Lustre is        │
│                                                                    │ consist of two main servers.                                       │
│                                                                    │                                                                    │
│                                                                    │  • Metadata server (MDS) stores and serves metadata of the file    │
│                                                                    │    system such as file names, permission information, and          │
│                                                                    │    directories. Each MDS is consist of one or more metadata        │
│                                                                    │    targets (MDT) which are disks used to store actual data.        │
│                                                                    │  • Object storage server (OSS) stores the file data on one or more │
│                                                                    │    object storage targets (OST). The maximum throughput and        │
│                                                                    │    capacity of OSS are a sum of each OST's maximum throughput and  │
│                                                                    │    capacity, respectively.                                         │
│                                                                    │                                                                    │
│                                                                    │ When a client creates and writes a new file, the file can be       │
│                                                                    │ distributed over multiple OSSes with different sized file chunks   │
│                                                                    │ which can be configured using stripeCount and stripeSize           │
│                                                                    │ parameters, respectively. By adjusting stripeCount, the client can │
│                                                                    │ improve the parallelism since multiple OSSes can be used in a      │
│                                                                    │ parallel manner. By adjusting stripeSize, the data from the        │
│                                                                    │ certain process can be stored in a contiguous space. The           │
│                                                                    │ performance of applications can be improved by several order of    │
│                                                                    │ magnitude with ideal stripeCount and stripeSize [7].               │
│                                                                    │                                                                    │
│                                                                    │ This analysis shows that even at the HPC environment where users   │
│                                                                    │ can exploit far more OSTs compared with the traditional computing  │
│                                                                    │ environment, users do not adjust Lustre file system configuration  │
│                                                                    │ and dynamic configuration control is needed to fully exploit the   │
│                                                                    │ I/O capabilities of HPC environment.                               │
│                                                                    │                                                                    │
│                                                                    │ In addition, we also analyzed the number of unique applications    │
│                                                                    │ among 1284643 runs. This is done by querying the database on       │
│                                                                    │ distinct application name. The result shows that there are only    │
│                                                                    │ 1163 unique applications which were executed during the two-month  │
│                                                                    │ period. Since there are 1284643 executions during that period, it  │
│                                                                    │ shows that the small number of applications was executed multiple  │
│                                                                    │ times. Thus, by utilizing information from the previous execution, │
│                                                                    │ the performance of each additional execution can improve the       │
│                                                                    │ performance since there is a high chance that the application will │
│                                                                    │ run in the near future.                                            │
├────────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────┤
```

### Deleting a Trace

```bash
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
