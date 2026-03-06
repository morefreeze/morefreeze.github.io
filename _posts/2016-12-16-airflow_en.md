---
layout: post
title: "Airflow Quick Start Guide"
description: ""
category: tech
comments: true
tags: [tech, airflow, pip, python]
---
{% include JB/setup %}

* Table of Contents
{:float-toc}

Lately I've been tormented by online tasks that keep failing in various ways, causing logs to go missing or scripts to fail execution. When problems occur, I have to manually fix them - like补 missing logs or re-running failed scripts. Some scripts have dependencies between them, so running them manually is complicated. I have to check back periodically to see if a script has finished before running the next one, which seriously impacts efficiency.

So I thought, wouldn't it be great if there was a program that could help me define task dependencies, automatically handle runtime dependencies, and provide a visual interface to monitor execution status and manage tasks? Recently I found an open source project that meets all these requirements - airflow.
<!--more-->

---

## Installation

Installing Airflow is extremely simple with `pip`:

```shell
export AIRFLOW_HOME=~/airflow
pip install airflow[slack]
airflow initdb
```

The `slackclient` installed via pip is optional and only needed if you want to send notifications to Slack. However, I highly recommend installing it as well so you can receive timely task execution status reports.

## Quick Start

I have to say, Airflow's documentation is very comprehensive, covering everything from quick start guides to detailed explanations of the framework's concepts.

After reading the official [tutorial](https://airflow.incubator.apache.org/tutorial.html), you'll be ready to start working. As mentioned earlier, I need to first set some properties for a DAG object, such as retry strategy, start/end times, execution environment, etc., like this:

{% highlight python linenos  %}
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime(2015, 6, 1),
    'email': ['morefreeze@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=5),
    # 'end_date': datetime(2016, 1, 1),
}
{% endhighlight %}

The parameters are mostly self-explanatory. The third line `depends_on_past` indicates whether to depend on the execution status of the previous run of itself.

If you configure email-related settings, you'll need to configure the outgoing mail server in `airflow.cfg`.

Since this task will run continuously, I've commented out the end date.

The above only configures the DAG parameters. Next, let's create a dag object:

```python
dag = DAG(
    'tutorial', default_args=default_args, schedule_interval='* * * * *')
```

I modified the official example here. `schedule_interval` indicates the execution frequency.

I changed it to crontab format, which is more intuitive and easier to modify. Airflow also provides some literal values to represent execution intervals, like `@hourly`, which will run the script at minute 0 of every hour. However, if you're running tasks in production, we usually stagger the execution of different scripts instead of running all of them at minute 0 of every hour. So I recommend using the crontab format.

Now let's define the tasks. Actually, defining tasks is like writing a shell script, except each operation can have dependencies.

Different operations correspond to different Operators. For example, shell commands need to be executed using BashOperator. Like this:

{% assign ds = "{{ ds }}" %}

```python
t1 = BashOperator(
    task_id='print_date',
    bash_command='date',
    dag=dag)


text = '{{ ds }} [%s] has been done' % (dag.dag_id)
t2 = SlackAPIPostOperator(
    task_id='post_slack',
    token='xoxp-your-key-here',
    channel='#random',
    username='airflow',
    text=text,
    dag=dag
)

t1 >> t2  # t2.set_upstream(t1)
```

I modified the example again. This DAG contains two tasks: t1 and t2. t1 is a shell command that calls `date` to display the current time.
t2 is an operation that sends a message to [slack](https://slack.com). You need to set a slack token, which can be obtained from [here](https://api.slack.com/web). Then set the channel and username to post to - you can keep the defaults. To send Slack messages, you need to have installed slackclient during installation.

Looking at the message text `text`, Airflow commands or messages like this support jinja2 template language. `{{ ds }}` is a macro that represents the current date in the format `2016-12-16`. Supported macros can be found [here](https://airflow.incubator.apache.org/code.html#macros).

The last line sets up the dependency relationship. Obviously, t1 executes first, and t2 executes after t1 completes. You can also use the commented syntax, but I find `>>` more intuitive. Conversely, there's also `<<`.

If you have multiple dependencies, just write them on separate lines like this:

```python
t1 >> t
t3 >> t << t2
t >> w >> x
```

The dependency graph above looks like this:

```
t1 ---+
t2 ---+--> t ---> w ---> x
t3 ---+
```

Congratulations! You've successfully created your first DAG. Now you can start execution!

## Commands

All Airflow execution operations need to be done on the command line. I have to complain here - the interface can only show task dependencies and execution status, but if a task fails, you still have to use the command line to fix it. This is a bit user-unfriendly (of course, you can submit a PR for this :P).

Overall, Airflow commands are quite intuitive. The commonly used ones are as follows:

- test: Used to test a specific task without requiring dependencies to be met
* run: Used to execute a specific task, requires dependencies to be met
* backfill: Executes a specific DAG, automatically resolves dependencies and executes in order
* unpause: Starts a DAG as a recurring task (it's off by default, so be sure to execute this command after writing your DAG file). The opposite command is pause
* scheduler: This is Airflow's scheduling program, usually started in the background
* clear: Clears the status of some tasks, allowing the scheduler to re-run them

From the order of the commands above, you can see my typical execution flow: After writing the DAG file, I directly use the backfill command to test if the entire DAG works. If individual tasks fail, I check the logs to fix the errors. At this point, I can use test to execute them individually, or run if there are dependencies. Once everything is working, I use unpause to enable periodic execution. Of course, the scheduler should already be running in the background. If I need to re-run tasks later, I use the clear command.

## Some Concepts

Earlier I was in a hurry to introduce Airflow examples and skipped over some basics. Let's go back and补充 some fundamental concepts.

### DAG (Directed Acyclic Graph)

It represents a collection of tasks, describing the dependencies between tasks and some properties of the entire DAG, such as start/end times, execution intervals, retry strategies, etc. Usually, one .py file is one DAG.

You can also think of it as a complete shell script that ensures commands execute in order.

### task

These are the individual Operators in the DAG file, describing specific operations.

### Operator

Airflow defines many Operators. Usually, one operation corresponds to a specific Operator. For example, use BashOperator to call shell commands, PythonOperator to call Python functions, EmailOperator to send emails, SSHOperator to connect via SSH. The community is constantly contributing new Operators.

### ds (Date String)

Earlier the script used the `{{ ds }}` variable. Each time a DAG is executed, a specific time (datetime object) is passed in.
This `ds` will be replaced with the corresponding time when rendering the command. I need to emphasize this:
For periodic tasks, Airflow passes in the time of **the previous period** (this is important). For example, if your task runs daily,
today it will pass in yesterday's date. If it's a weekly task, it will pass in the date from one week ago today.

### Macros

The previous section mentioned the `ds` variable. You're probably wondering what to do if your script needs different time formats or different time periods.
This is where Macros come in. Airflow itself provides several time formats, like `ds_nodash` (as the name suggests, a date format without hyphens `-`).
There are also related functions you can call directly, like `ds_add` which can add or subtract time.

## Airflow Configuration

Earlier, to quickly demonstrate Airflow's power, I skipped many things like its configuration.

When Airflow initializes, it automatically generates an `airflow.cfg` file in the `AIRFLOW_HOME` directory. Let's open it and look at its structure.

### executor

This is Airflow's most critical configuration, indicating how Airflow executes tasks. There are three options:

- SequentialExecutor: Single-process sequential execution, usually only used for testing
- LocalExecutor: Multi-process local execution, uses Python's multi-processing library to achieve parallel task execution
- CeleryExecutor: Uses celery as the executor. With proper celery configuration, tasks can be run distributed across multiple machines. Generally used in production environments.

### sql_alchemy_conn

This configuration specifies how Airflow stores metadata. The default is sqlite. For production deployment, I recommend using mysql.

### smtp

If you need email notifications or use the EmailOperator, you need to configure the outgoing SMTP server.

### celery

As mentioned earlier, when using CeleryExecutor, you need to configure the celery environment.

## Summary

Suddenly I realize I've written a lot, but this should be enough for daily needs. I'll stop here for now and save some advanced techniques and practical issues encountered in production for another article [Airflow Advanced Guide](/2017/02/airflow-advance.html).