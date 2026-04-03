# Lab 2 Reflection

In this lab, both containers ran on your laptop. In production, the preprocessor would run in the warehouse datacenter and the inference API would run in Congo's main datacenter.

**How would the architecture and your `docker run` commands differ if these containers were actually running in separate datacenters?**

Consider:
- How would the preprocessor find the inference API?
- What about the shared volumes?
- What new challenges would arise?


## Your Reflection Below

### How Lab Architecture Differs from Real-World Distributed Systems

When I was doing this lab, both containers were running on my laptop, which made everything simple. But it got me thinking—what happens when the preprocessor is sitting in Congo's warehouse datacenter trying to talk to the inference API thousands of miles away in the main datacenter? That's way more complicated.

**1. Finding the API (Service Discovery)**

Right now, I'm hardcoding `API_URL=http://host.docker.internal:8000` because everything is local. But in production, that completely breaks down. I can't just say "go to host.docker.internal" when the preprocessor is literally on a different server in a different building.

Instead, we'd probably use:
- A DNS name (like `api.congo-returns.internal`) that resolves to wherever the API actually is
- A load balancer in front of the API so if one server goes down, requests go to another one
- Some kind of service discovery tool that keeps track of where the API is running
- Everything encrypted with TLS because data traveling between datacenters can't be sent in plain text

So my docker command would change from pointing to localhost to pointing to a domain name or load balancer URL somewhere in the main datacenter.

**2. The Storage Problem (Volumes Don't Work Across Datacenters)**

This is something I didn't fully appreciate until I thought about it. The `-v` volume mount looks simple when everything is on one machine. But imagine the warehouse trying to write to `/incoming/` and the main datacenter trying to access those same files—that's impossible with local volumes.

Here's what would actually need to happen:
- Images get uploaded to something like AWS S3 or Azure Blob Storage (cloud storage)
- Instead of writing to JSONL files, logs go to a real database (PostgreSQL, MongoDB)
- We could use NFS (network file storage) but that seems risky and slow across datacenters

The docker run commands wouldn't have `-v` mounts anymore. Instead, we'd pass AWS keys or database credentials as environment variables.

**3. Communication Gets Tricky**

Right now the preprocessor just makes an HTTP request to the API and waits for the answer. That works fine in the lab, but what if the API is down for maintenance or having problems? The preprocessor would just fail.

In a real system, I'd probably:
- Have the preprocessor send messages to a queue (RabbitMQ, Kafka, AWS SQS) instead of calling HTTP directly
- The API would pull messages from that queue and process them
- Results would go back into a results queue
- The preprocessor would check the results queue when done

This way if the API is temporarily down, messages just sit in the queue and get processed when it comes back up. Much more robust than what we have here.

**4. Logging and Monitoring**

With everything locally, I can just look at JSONL files on my machine. But across datacenters, I'd need something like Datadog or the ELK Stack where all logs from all containers go to one central place. That way I can actually debug problems that span both datacenters.

**5. Security (The Stuff They Don't Teach in Beginner Courses)**

I didn't think much about this in the lab, but in production:
- Data traveling between datacenters has to be encrypted (TLS)
- Containers need to authenticate to each other somehow (API keys or certificates)
- We might need to make sure customer data stays in certain countries (compliance rules)
- Someone has to audit who accessed what data

### So What Did I Learn?

| What I Did (Lab):
What Real Production Does
Hardcoded localhost, DNS names and load balancers, Local volume mounts, Cloud storage (S3) + databases, Simple HTTP requests, Message queues + async processing, Log files on my machine, Centralized logging platforms, No encryption needed, TLS everywhere



