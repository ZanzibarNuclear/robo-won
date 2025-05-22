# Flux Moderator Agents

This a set of agents designed to moderate content on the World of Nuclear platform.

## Motivation

Flux is a social media type of feature in the World of Nuclear. Members are allowed to post whatever they wish for all the world to see. That is great from a freedom of expression perspective. It also opens the door for abuse by trolls and other bad actors.

In the old days, companies would employ human moderators to review posts and decide which have crossed the line. They might even decide to ban a user who is being abusive and otherwise violating the terms of use.

These days, a better idea is to use AI agents who can do the task automatically and will not suffer the trauma of embarrassment or fatigue from dealing with difficult people.

## Agents

The first agent will read posts and flag any that seem to cross the line of decency, which is the primary vector of the terms of use.

Let's see how this goes. Other agents will follow.

## Running as a Service

The flux_agents can be run as a service on Linux systems using either the provided controller script or systemd.

### Using the Controller Script

The `won_agent_service.py` script provides a simple way to manage the flux_agents service:

```bash
# Make the script executable (if not already)
chmod +x won_agent_service.py

# Start the service
./won_agent_service.py start

# Check the status
./won_agent_service.py status

# Stop the service
./won_agent_service.py stop

# Restart the service
./won_agent_service.py restart
```

The service will write logs to the location specified by `LOG_FILE` in the settings, and will store its PID in the file specified by `PID_FILE`.

### Using systemd (Recommended for Production)

For a more robust service management on Linux systems that use systemd:

1. Edit the provided `won-agents.service` file:

   - Update the `User` field with the appropriate username
   - Update the `WorkingDirectory` and `ExecStart` paths to match your installation

2. Install the service:

   ```bash
   # Copy the service file to the systemd directory
   sudo cp flux_agents.service /etc/systemd/system/

   # Reload systemd to recognize the new service
   sudo systemctl daemon-reload

   # Enable the service to start on boot
   sudo systemctl enable won-agents

   # Start the service
   sudo systemctl start won-agents
   ```

3. Managing the service:

   ```bash
   # Check status
   sudo systemctl status flux-agents

   # Stop the service
   sudo systemctl stop flux-agents

   # Restart the service
   sudo systemctl restart flux-agents

   # View logs
   sudo journalctl -u flux-agents
   ```

### Configuration

The service uses environment variables for configuration, which can be set in the `.env` file:

- `WON_SERVICE_ENDPOINT`: API endpoint for the World of Nuclear service
- `WON_SERVICE_API_KEY`: API key for authentication
- `OLLAMA_HOST`: Host address for Ollama
- `LLM_MODEL`: The LLM model to use
- `POLLING_INTERVAL`: Time in seconds between polling cycles (default: 60)
- `LOG_FILE`: Path to the log file (default: ./flux-moderator.log)
- `PID_FILE`: Path to the PID file (default: ./flux-moderator.pid)
