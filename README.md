# Paperboy-LFL

## Overview
Paperboy-LFL is an automated tool for monitoring academic publications. It searches RSS feeds for specified keywords and authors, then pushes matching articles in a readable format to a designated Slack channel. This automation is fully handled via GitHub Actions.

## Getting Started

### Prerequisites
- A GitHub account
- A Slack workspace with a bot user

### Setup

#### Slack Bot User
1. Create an app in your Slack workspace by visiting [Slack API](https://api.slack.com/apps).
2. Enable the Slack bot user.
3. Install the app to your workspace and copy the bot user token from the 'OAuth & Permissions' tab.
4. Add the bot user token as a secret in your GitHub repository (named `SLACK_TOKEN`).

#### GitHub Repository
1. Fork the Paperboy-LFL repository to your GitHub account.
2. Clone the forked repository to your local machine for configuration.

#### Configuration Files
- `authors.txt`: List authors to track. Include variations of names with/without middle initials.
- `feeds.txt`: URLs of RSS feeds to monitor.
- `keywords.txt`: Keywords to search within the articles.
- `channel.txt`: Slack channel ID where the articles will be posted.

#### Updating Configuration Files
1. Modify `authors.txt`, `feeds.txt`, `keywords.txt`, and `channel.txt` as needed in your forked repository.
2. Commit and push the changes to your GitHub repository.

### GitHub Actions
- The workflow is set up in `.github/workflows/schedule.yml`.
- The action is scheduled to run at a specified time every day.
- On execution, the script `distributor.py` processes the RSS feeds and sends the relevant articles to the specified Slack channel.

## Contributing
To add more keywords, feeds, or authors:
1. Fork the repository.
2. Modify `keywords.txt`, `feeds.txt`, or `authors.txt` as needed.
3. Commit and push your changes to your forked repository.
4. Create a pull request for your changes to be reviewed and merged into the main repository.

## Important Notes
- Avoid overwhelming your Slack channel with repeated messages during initial setup and testing. Consider using a private channel for testing.
- Follow best practices when making contributions to the project via pull requests.

