# Selective Disclosure: Giving AI Agents Access to an ERP Without Drowning Them

Over the last year I designed and built an MCP runtime that gives AI agents governed access to NetSuite. The hardest problem was not authentication or execution. It was deciding how much of the system to show the agent at once. This post describes the pattern I landed on, which I call selective disclosure, and the tradeoffs that came with it.

## The problem

An ERP is enormous. A mid-sized NetSuite account has hundreds of record types, thousands of fields, and decades of accumulated customizations. When we started exposing business operations to agents, the obvious approach was to register each operation as its own tool: one tool for creating a sales order, one for looking up inventory, one for printing a receiving label, and so on. This fails in two ways.

The first is context. Every tool definition you register is text the model has to read on every request. A catalog of 50 business operations, each with a full parameter schema, consumes a large share of the context window before the agent has done anything. Worse, tool selection accuracy degrades as the catalog grows. An agent choosing between 6 tools is reliable. An agent choosing between 80 similar-sounding ERP operations is not.

The second is coupling. NetSuite's AI Connector imposes its own CustomTool schema, and that schema changed across releases while we were building. If every business operation is registered directly against that surface, every schema change touches every tool. We would be rewriting the catalog each time the platform moved underneath us.

## The design

Instead of exposing every operation, the runtime exposes a small set of stable meta-tools. The agent sees roughly half a dozen functions, and they do not change when the business catalog changes:

1. **List tools** returns a summary of the operations available to the current user: name, category, and a one-line description. No parameter schemas.
2. **List categories** and **list tools by category** let the agent narrow down when the catalog is large.
3. **Get tool schema** returns the full parameter schema for one operation, or a requested list of operations, on demand.
4. **Execute operation** runs a single named operation with structured parameters through one dispatcher.

The agent's workflow becomes progressive: discover what exists, fetch details only for the operations it intends to use, then execute. The detailed schemas enter the context only when they are needed, and only for the tools that matter to the current task.

Behind that surface sits a plugin architecture. The core runtime owns discovery, permission filtering, schema shaping, and execution dispatch. The business operations themselves live in separate plugin-pack SuiteApps. Each plugin registers a namespaced operation name, a description, a parameter schema, and a handler. The plugin catalog is stored in NetSuite records and queried with SuiteQL at discovery time, so installing a plugin pack is enough to make its tools appear. Nothing in the shared runtime changes.

Permissions ride along with discovery. The plugin loader filters the catalog by role and user before the agent ever sees the tool list. An agent acting for a warehouse user does not see finance operations, and does not need to be told not to use them. The tools simply are not there. This turned out to be one of the strongest arguments for the pattern: access control happens once, in the runtime, instead of being restated in every agent prompt.

The coupling problem is solved by the same boundary. Only the small meta-tool surface touches NetSuite's CustomTool schema. When that schema changed, we absorbed the change in one adapter layer, and none of the plugin packs noticed.

## Results

The runtime is deployed in production client accounts and is the foundation for our AI consulting engagements. Three plugin packs currently register tools into it: a general-purpose pack, a pack for our own products, and a client-vertical pack. A typical engagement starts by installing the core and delivering a small set of high-value operations for that client's workflows. The client gets immediate use cases, and the platform grows by adding plugins rather than by re-architecting.

The context savings are what you would expect. The agent carries a handful of stable function definitions instead of the full catalog, and pulls perhaps two or three schemas per task. Tool selection stays reliable because the agent chooses from short summaries first and commits to details second.

## Tradeoffs

Selective disclosure is not free.

The main cost is round trips. A direct-registered tool can be called in one step. Under this pattern the agent may need three calls before the first real action: list, get schema, execute. For short tasks the overhead is noticeable. In practice agents cache well within a conversation, so the cost is paid once per session rather than once per action, but it is real.

The pattern also depends on the quality of the tool summaries. The agent picks operations from one-line descriptions, so a vague description produces wrong tool choices that a full schema might have prevented. We ended up treating description writing as a design activity, not documentation.

Finally, a single dispatcher means execution errors have to be structured. If a handler throws, the AI Connector sees a generic failure and the agent learns nothing. The dispatcher instead returns error payloads that describe what was invalid, so the agent can correct its parameters and retry. Getting this right took more iteration than the happy path did.

## Why I think this generalizes

Nothing here is specific to NetSuite. Any system with a large operation surface, an ERP, a CRM, an internal API catalog, faces the same choice when connecting agents: show everything and pay in context and accuracy, or show a discovery layer and pay in round trips. For catalogs beyond a few dozen operations, I think the second trade wins, and MCP makes the pattern natural to express. The interesting engineering is not in the protocol. It is in deciding what the agent gets to see, and when.
