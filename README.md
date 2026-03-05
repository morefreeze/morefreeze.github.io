Freshman21
==========

Freshman21 is a Jekyll blog theme, base on theme [Freshman](http://github.com/yulijia/freshman).

A tribute to WordPress Theme Twenty-Twelve and Twenty-eleven.

Enjoy.


![Screen](http://i.imgur.com/oSp7kacl.png)

### Version 2.0 update 2015.03.31

- master branch: the simplest template, original version.

- gh-pages branch: master branch with google analytics js template, BackToTop js script, readmore module.

Clone master branch:

`git clone https://github.com/yulijia/freshman21.git -b master --single-branch`

Clone gh-pages branch:

`git clone https://github.com/yulijia/freshman21.git -b gh-pages --single-branch`


### How to install this theme?

```
# please make sure you have already installed git tools and ruby tools(gem)
# make sure use pyenv activate environment
$ gem install sass webrick
$ gem install jekyll jekyll-paginate
$ pip install simiki
```

### A Summary of Features

- Provide single column and two columns layout
- Powerful configure file
- Comments by Disqus
- Support LaTeX (by MathJax)
- Syntax highlighting


### Demo

Single column, please see [my own blog](http://yulijia.net/en/)

Two columns, please see the [theme website](http://yulijia.net/freshman21/)


# Blog Content Generation Pipeline

An automated blog content generation pipeline that integrates with Logseq for idea capture and uses multiple AI agents to handle different stages of content creation.

## Features

- **Logseq Integration**: Automatically sync content from Logseq to blog drafts
- **AI-Powered Content Generation**: Multiple specialized agents for research, writing, editing, and social media
- **Human Review Process**: All AI-generated content goes through human review before publishing
- **Multi-Platform Distribution**: Automatically generate social media content for X/Twitter, Xiaohongshu, and GitHub

## Quick Start

### Prerequisites

- Python 3.8+
- Git
- Logseq (optional, for idea capture)
- API keys for AI services (Anthropic/OpenAI)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/your-blog.git
cd your-blog
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

4. **Set up Logseq sync (optional)**:
   - Configure Logseq Git sync
   - Update `logseq_config.json` with your Logseq repository path

### Basic Usage

#### Option 1: Manual Workflow

1. **Create a draft manually**:
```bash
# Create a new draft in _drafts/
echo "# My New Post" > _drafts/my-new-post.md
```

2. **Generate content using Claude Code**:
   - Open the draft in your editor
   - Use Claude Code to expand, research, or edit the content
   - Review and refine the generated content

3. **Publish the draft**:
```bash
# Move from _drafts/ to _posts/ with proper naming
mv _drafts/my-new-post.md _posts/$(date +%Y-%m-%d)-my-new-post.md
```

#### Option 2: Automated Pipeline (Advanced)

1. **Sync from Logseq**:
```bash
python scripts/logseq_sync.py
```

2. **Generate content**:
```bash
python agents/orchestrator.py
```

3. **Review and manage drafts**:
```bash
# List drafts for review
python scripts/draft_manager.py list pending

# Approve a draft
python scripts/draft_manager.py approve draft-filename.md
```

### Using Claude Code for Content Creation

The simplest and most effective workflow:

1. **Start with an idea**:
   - Write a brief outline or bullet points in `_drafts/`
   - Include key points, sources, and your perspective

2. **Use Claude Code to expand**:
   ```bash
   # In Claude Code, use commands like:
   /read _drafts/my-idea.md
   "Expand this into a full blog post with introduction, body, and conclusion"
   ```

3. **Review and edit**:
   - Read the generated content
   - Add your personal voice and experiences
   - Fact-check any claims or data

4. **Publish**:
   ```bash
   # Move to _posts/ with proper date prefix
   git add _posts/
   git commit -m "Add new post: Title"
   git push
   ```

### Draft Management

The `_drafts/` directory structure:
```
_drafts/
├── for_review/      # Drafts ready for human review
├── approved/        # Approved drafts
├── rejected/        # Rejected drafts
└── *.md            # Work-in-progress drafts
```

### GitHub Actions

The repository includes GitHub Actions for:
- **Daily Logseq sync** (if configured)
- **Content generation** (when drafts are added)
- **Publishing** (when drafts are approved)

Both workflows can be triggered manually from the GitHub Actions tab.

## Architecture

### System Components

1. **Logseq Integration**: Git-based sync for capturing ideas and initial content
2. **Main Orchestrator Agent**: Coordinates the entire pipeline workflow
3. **Specialized Sub-Agents**:
   - Research/Outline Agent
   - Content Writing Agent
   - Editing/Optimization Agent
   - Social Media Distribution Agent
4. **Draft Management**: All content goes through `_drafts/` folder for human review

### Directory Structure

```
├── _drafts/                    # AI-generated content awaiting review
│   ├── for_review/            # Drafts ready for human review
│   ├── approved/              # Approved drafts
│   └── rejected/              # Rejected drafts
├── _posts/                     # Published blog posts
├── agents/                     # AI agent implementations
│   ├── orchestrator.py        # Main coordination logic
│   ├── research_agent.py      # Research and outline generation
│   ├── writing_agent.py       # Content writing
│   ├── editing_agent.py       # Editing and optimization
│   ├── social_agent.py        # Social media content
│   └── config.py              # Configuration
├── scripts/                    # Automation scripts
│   ├── logseq_sync.py         # Logseq synchronization
│   └── draft_manager.py       # Draft lifecycle management
├── .github/workflows/          # GitHub Actions
│   ├── logseq-sync.yml        # Automated Logseq sync
│   └── content-generation.yml # Content generation pipeline
├── logseq_config.json          # Logseq sync configuration
├── .env.example               # Environment variables template
└── requirements.txt           # Python dependencies
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# AI Provider Settings
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Logseq Settings
LOGSEQ_REPO_PATH=/path/to/logseq

# Blog Settings
BLOG_REPO_PATH=.
DRAFTS_DIR=_drafts
POSTS_DIR=_posts
```

### Logseq Configuration

Edit `logseq_config.json` to customize:

```json
{
  "logseq_repo_path": "/path/to/logseq",
  "blog_repo_path": ".",
  "drafts_dir": "_drafts",
  "blog_tags": ["#blog-idea", "#draft", "#blog"],
  "asset_extensions": [".png", ".jpg", ".jpeg", ".gif"]
}
```

## Usage Examples

### Content Generation Workflow

1. **Capture ideas in Logseq**: Tag pages or blocks with #blog-idea
2. **Sync to blog**: Run `python scripts/logseq_sync.py`
3. **Generate content**: Run `python scripts/content_pipeline.py`
4. **Review drafts**: Check `_drafts/for_review/` folder
5. **Approve content**: Use `python scripts/draft_manager.py approve <filename>`
6. **Publish**: Approved drafts can be published to `_posts/`

### Draft Management Commands

```bash
# List all drafts
python scripts/draft_manager.py list

# List drafts pending review
python scripts/draft_manager.py list pending

# Move a draft to review folder
python scripts/draft_manager.py review draft-filename.md

# Approve a draft (moves to approved folder)
python scripts/draft_manager.py approve draft-filename.md

# Approve and publish a draft
python scripts/draft_manager.py approve draft-filename.md true

# Reject a draft
python scripts/draft_manager.py reject draft-filename.md "Reason for rejection"

# View analytics
python scripts/draft_manager.py analytics

# Generate review report
python scripts/draft_manager.py report
```

## GitHub Actions

### Automated Logseq Sync

The pipeline includes a GitHub Action (`.github/workflows/logseq-sync.yml`) that:
- Runs daily at 2 AM UTC
- Syncs content from Logseq to blog drafts
- Triggers content generation on new drafts

### Manual Triggers

Both workflows can be triggered manually from the GitHub Actions tab.

## Development

### Adding New Agents

To add a new specialized agent:

1. Create a new file in `agents/` (e.g., `new_agent.py`)
2. Implement the agent class with a `process()` method
3. Add configuration to `agents/config.py`
4. Integrate into the orchestrator in `agents/orchestrator.py`

### Customizing Prompts

Edit the system prompts in `agents/config.py` to customize the behavior of each agent. Each agent has its own system prompt that defines its role and responsibilities.

## Monitoring and Analytics

The draft management system tracks:
- Total drafts created
- Approval/rejection rates
- Average review time
- Monthly creation trends

View analytics with:
```bash
python scripts/draft_manager.py analytics
```

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all API keys are set correctly in `.env`
2. **Logseq Sync Issues**: Check that the Logseq repository path is correct
3. **Content Generation Failures**: Check the logs in the `logs/` directory
4. **Draft Management Errors**: Ensure file permissions are correct

### Debug Mode

Run agents with debug logging:

```bash
# Set debug environment variable
export DEBUG=1
python agents/orchestrator.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in the `logs/` directory
3. Open an issue on GitHub
