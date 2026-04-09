# Realtor Blog CMS

A lightweight content management system for reviewing and publishing AI-generated blog posts. Built for content creators who use Claude Code (or any AI) to research topics, generate SEO-optimized blog posts, and manage their publishing pipeline -- all backed by Supabase.

**Stack:** React 19 + Vite + Tailwind CSS 4 + Supabase (all free tier)

## Features

- **Blog post management** -- Draft, review, and publish posts with a clean editor interface
- **Topic research pipeline** -- Research keywords and topics with Claude Code, save them to the CMS, review and approve, then write
- **AI-native workflow** -- CLAUDE.md teaches Claude Code your database schema, content block format, and pipeline commands
- **Inline editing** -- Click any text block in the preview to make quick corrections
- **SEO metadata** -- Title, meta description, keywords, and slug editing with character counts
- **Deploy hooks** -- Automatically trigger a site rebuild when you publish a post
- **Scheduling** -- Set a future publish date and posts show as "Scheduled"
- **Settings page** -- Configure your brand name, site URL, default author, and more (saved to localStorage)
- **Row Level Security** -- Authenticated users manage everything; public API only returns published posts

## Prerequisites

- **Node.js 18+** -- [Download here](https://nodejs.org/)
- **Supabase account** -- [Sign up here](https://supabase.com/) (free tier is plenty)
- **Claude Code** (optional but recommended) -- [Get it here](https://claude.ai/download)
- **Vercel account** (for deployment) -- [Sign up here](https://vercel.com/) (free tier works)

## Quick Start

### 1. Use this template

Click **"Use this template"** on GitHub, or fork the repo:

```bash
git clone https://github.com/YOUR_USERNAME/claude-code-knowledge-base-kit.git
cd claude-code-knowledge-base-kit
npm install
```

### 2. Create a Supabase project

1. Go to [app.supabase.com](https://app.supabase.com)
2. Click **New Project**
3. Give it a name (e.g., "blog-cms") and set a database password
4. Wait for it to finish setting up (~1 minute)

### 3. Run the database migrations

1. In your Supabase dashboard, go to **SQL Editor**
2. Click **New query**
3. Copy the contents of `supabase/migrations/001_blog_posts.sql` and paste it in
4. Click **Run** (you should see "Success. No rows returned")
5. Repeat with `supabase/migrations/002_blog_topics.sql`

### 4. Create your CMS user

1. In your Supabase dashboard, go to **Authentication** > **Users**
2. Click **Add user** > **Create new user**
3. Enter your email and a password
4. Check "Auto Confirm User"
5. Click **Create user**

### 5. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` with your Supabase credentials:

1. Go to **Settings** > **API** in your Supabase dashboard
2. Copy your **Project URL** and **anon/public key**
3. Paste them into `.env`:

```
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...
```

### 6. Start the dev server

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) and sign in with the user you created in step 4.

### 7. Deploy to Vercel

```bash
npm run build
```

Deploy the `dist/` folder to Vercel (or any static host):

1. Push your repo to GitHub
2. Go to [vercel.com/new](https://vercel.com/new) and import the repo
3. Add your environment variables (`VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`)
4. Deploy

**Optional: Custom subdomain**

Point `cms.yourdomain.com` to your Vercel deployment:

1. In Vercel, go to your project **Settings** > **Domains**
2. Add `cms.yourdomain.com`
3. Add the CNAME record to your DNS provider

### 8. Set up deploy hooks (optional)

To automatically rebuild your website when you publish a post:

1. Create a deploy hook in Vercel: Dashboard > Your Site Project > Settings > Git > Deploy Hooks
2. Add it to your `.env` (and Vercel environment variables):
   ```
   VITE_DEPLOY_HOOK_URL=https://api.vercel.com/v1/integrations/deploy/...
   ```
3. Now when you save a post with status "Published", it triggers a rebuild of your main site

## Claude Code Setup

### How the CLAUDE.md works

The `CLAUDE.md` file in the project root teaches Claude Code:

- **Your database schema** -- table names, column types, and relationships
- **The topic pipeline** -- how to save researched topics, write approved ones, and check for CMS changes
- **The research_data JSONB format** -- a consistent structure for SEO research payloads
- **Content block types** -- the JSON format the CMS expects for blog post content

When you open Claude Code in this project directory, it reads `CLAUDE.md` automatically. You can then use natural language commands like:

### Example workflows

**Research topics:**
```
Research 5 blog topics about [YOUR NICHE]. Include keyword data,
competitor analysis, and content gaps. Then put them in the CMS.
```

Claude Code will research the topics and INSERT them into `blog_topics` with full keyword metrics and research data. You review them in the CMS Topics page.

**Write approved blogs:**
```
Write the approved topics from the CMS.
```

Claude Code queries `blog_topics` for approved items, writes each one as a structured blog post using the content block format, and inserts them into `blog_posts` as drafts.

**Check for CMS changes:**
```
I made changes in the CMS -- what's new?
```

Claude Code queries recent updates and reports what you changed (approved topics, edited posts, etc.).

**SEO review before publishing:**
```
Review the blog post "your-post-slug" for SEO quality before I publish it.
```

See the prompts in `prompts/seo-review.md` for the full SEO audit checklist.

## Customization

### Brand settings

Edit the defaults in `src/config.js`, or use the **Settings** page in the CMS to configure at runtime:

- Site/brand name
- Website URL
- Default author
- Blog path prefix
- YouTube channel URL

Settings are saved to localStorage so they persist across sessions without redeploying.

### Categories

Edit the `CATEGORY_OPTIONS` array in `src/components/MetadataSidebar.jsx` to match your content topics:

```js
const CATEGORY_OPTIONS = [
  'Neighborhoods',
  'Market Update',
  'Home Buying',
  'Lifestyle',
  // Add your own...
];
```

### Content block types

The CMS supports 12 block types out of the box. See `CLAUDE.md` for the full reference. To add a new block type:

1. Add the render case in `src/components/ContentRenderer.jsx`
2. Document it in `CLAUDE.md` so Claude Code knows how to use it

### Knowledge base

See `prompts/setup-knowledge-base.md` for instructions on setting up a folder of your content (transcripts, emails, past posts) so Claude Code can match your voice when writing.

## Connecting to Your Website

The CMS stores content in Supabase. Your website reads from the same database to display published posts.

**Fetching published posts (example):**

```js
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// Get all published posts
const { data: posts } = await supabase
  .from('blog_posts')
  .select('*')
  .eq('status', 'published')
  .order('date', { ascending: false })

// Get a single post by slug
const { data: post } = await supabase
  .from('blog_posts')
  .select('*')
  .eq('slug', 'your-post-slug')
  .eq('status', 'published')
  .single()
```

The RLS policies ensure that unauthenticated (anon) requests can only read published posts, while authenticated users (you in the CMS) can read and edit everything.

## Block Types Reference

| Type | Fields | Description |
|------|--------|-------------|
| `paragraph` | `text` | Regular paragraph |
| `heading` | `text` | H2 heading with blue left border |
| `subheading` | `text` | H3 subheading |
| `list` | `items[]` | Bulleted list |
| `callout` | `title`, `text` | Blue callout box |
| `quote` | `text`, `attribution` | Block quote |
| `image` | `src`, `alt`, `caption` | Image with optional caption |
| `table` | `headers[]`, `rows[][]` | Data table |
| `pros-cons` | `pros[]`, `cons[]` | Side-by-side pros and cons |
| `info-box` | `content`, `variant?` | Info or warning box |
| `stat-cards` | `cards[{number, label, sublabel?}]` | Statistics grid |
| `process-steps` | `steps[{title, text}]` | Numbered steps |

## Project Structure

```
claude-code-knowledge-base-kit/
├── CLAUDE.md                    # AI assistant instructions (the valuable part)
├── README.md                    # This file
├── package.json                 # Dependencies
├── vite.config.js               # Vite + Tailwind config
├── .env.example                 # Environment variables template
├── index.html                   # HTML entry point
├── supabase/
│   └── migrations/
│       ├── 001_blog_posts.sql   # Blog posts table schema
│       └── 002_blog_topics.sql  # Topic research pipeline schema
├── prompts/
│   ├── generate-blog-post.md    # Prompt: transcript to blog post
│   ├── seo-review.md            # Prompt: SEO audit before publishing
│   └── setup-knowledge-base.md  # Guide: set up your voice/style KB
└── src/
    ├── main.jsx                 # Entry point
    ├── App.jsx                  # Routes
    ├── index.css                # Tailwind imports
    ├── config.js                # Brand configuration (edit defaults here)
    ├── lib/
    │   └── supabase.js          # Supabase client
    ├── contexts/
    │   └── AuthContext.jsx      # Auth state management
    ├── pages/
    │   ├── Login.jsx            # Email/password login
    │   ├── Dashboard.jsx        # Post list + stats + filters
    │   ├── PostEditor.jsx       # Content preview + metadata editor
    │   ├── Topics.jsx           # Topic research pipeline list
    │   ├── TopicDetail.jsx      # Individual topic detail + research data
    │   └── Settings.jsx         # Brand/site configuration
    └── components/
        ├── Layout.jsx           # Sidebar navigation
        ├── ProtectedRoute.jsx   # Auth guard
        ├── PostCard.jsx         # Post preview card
        ├── TopicCard.jsx        # Topic preview card
        ├── ContentRenderer.jsx  # Block type renderer (12 types)
        ├── MetadataSidebar.jsx  # Post metadata + SEO fields
        └── StatusBadge.jsx      # Status label component
```

## FAQ

**Can I use this without Claude Code?**
Yes. You can write blog posts manually and paste the JSON blocks into Supabase, or use any AI tool to generate the content. The CMS is just a review/publishing interface.

**Do I need to pay for Supabase?**
No. The free tier includes 500MB of database storage, 50,000 monthly active users for auth, and unlimited API requests. That is far more than a blog CMS needs.

**Can multiple people use it?**
Yes. Create additional users in Supabase Auth. All authenticated users have full access to all posts.

**How do I deploy the CMS?**
Run `npm run build` and deploy the `dist/` folder to any static host (Vercel, Netlify, Cloudflare Pages, etc.). It is a client-side app -- no server needed.

**Is this only for real estate?**
No. The CMS is industry-agnostic. The categories, content types, and research pipeline work for any niche. Just edit the categories in `MetadataSidebar.jsx` and update the CLAUDE.md with your domain-specific context.

## License

MIT
