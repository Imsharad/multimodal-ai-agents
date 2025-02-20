polyglot-circuit-2fmzys


<a href="https://livekit.io/">
  <img src="./.github/assets/livekit-mark.png" alt="LiveKit logo" width="100" height="100">
</a>

# Python Multimodal Voice Agent

<p>
  <a href="https://cloud.livekit.io/projects/p_/sandbox"><strong>Deploy a sandbox app</strong></a>
  •
  <a href="https://docs.livekit.io/agents/overview/">LiveKit Agents Docs</a>
  •
  <a href="https://livekit.io/cloud">LiveKit Cloud</a>
  •
  <a href="https://blog.livekit.io/">Blog</a>
</p>

A basic example of a multimodal voice agent using LiveKit and the Python [Agents Framework](https://github.com/livekit/agents).

## Dev Setup

Clone the repository and install dependencies to a virtual environment:

```console
cd multimodal-agent-python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Set up the environment by copying `.env.example` to `.env.local` and filling in the required values:

- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `OPENAI_API_KEY`

You can also do this automatically using the LiveKit CLI:

```bash
lk app env
```

Run the agent:

```console
python3 main.py  dev
```

## Frontend Setup

If you want to run the accompanying LiveKit frontend, follow these steps:

```bash
# Navigate to the frontend directory
cd livekit-frontend

# Install dependencies using pnpm
pnpm install

# Start the development server
pnpm dev
```

Key requirements:
1. Ensure you have valid LiveKit credentials in your `livekit-frontend/.env.local` file:
   ```dotenv
   LIVEKIT_API_KEY=<your-api-key>
   LIVEKIT_API_SECRET=<your-api-secret>
   LIVEKIT_URL=wss://<your-subdomain>.livekit.cloud
   ```
2. The frontend is built with Next.js 14 (using the App Router) and leverages key dependencies such as:
   - @livekit/components-react
   - Next.js 14.2.24
   - React 18.3.1
   - Tailwind CSS for styling

This agent requires a frontend application to communicate with. You can use one of our example frontends in [livekit-examples](https://github.com/livekit-examples/), create your own following one of our [client quickstarts](https://docs.livekit.io/realtime/quickstarts/), or test instantly against one of our hosted [Sandbox](https://cloud.livekit.io/projects/p_/sandbox) frontends.

### Key Files
### Key Files

- `main.py`: This is the main entry point of the application. It uses the LiveKit Agents CLI to run the agent worker, setting up the necessary options and invoking the `entrypoint` function defined in `src/core.py`.
- `src/core.py`: This file contains the core logic of the multimodal voice agent. It defines the `entrypoint` function, which handles connecting to a LiveKit room, waiting for a participant, and initiating the multimodal agent. It also defines the `run_multimodal_agent` function responsible for creating and starting the `MultimodalAgent`.
- `src/functions/tools.py`: This file defines the `AssistantFunctions` class, which encapsulates the tools and functionalities that the multimodal agent can use. Currently, it includes an example function `get_weather` to demonstrate how to integrate external tools with the agent.

## Model Selection

You can choose between OpenAI and Gemini models by setting the `MODEL_TYPE` environment variable in `.env.local`.

- To use OpenAI model, set `MODEL_TYPE="openai"`. This is the default if the variable is not set.
- To use Gemini model, set `MODEL_TYPE="gemini"`.

Make sure you have the corresponding API key set in `.env.local`:

- `OPENAI_API_KEY` for OpenAI model.
- `GEMINI_API_KEY` for Gemini model.
