# How to be more ambitious: A tutorial for humans with models

- **Author:** Felix Rieseberg (engineering manager at Anthropic, working on Claude)
- **Published:** 13 October 2026 (the page gives an 8-minute reading time)
- **Original, for the full text:** https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/

This file is a summary in our own words, not the essay. Phrases in quotation marks are the essay's own wording; everything else paraphrases it. Section headings follow the essay's order.

## Summary

### Why the essay exists

The author works on Claude and keeps seeing things done with models that he had not thought of or thought possible; his examples from the month of writing are a model that may have helped discover a new planet, the first AI music video he likes, and talk of a new era in mathematics. Citing Terence Tao, he notes that model capabilities grow unevenly, "astounding in some directions, while inadequate in others". Some users exploit the strong directions and achieve a lot; many others use models only for trivia or for softening the tone of an email. People who build AI often tell users to be more ambitious, but that advice is hard to act on, so the essay sets out to be a practical tutorial for it. The author uses Claude but says the advice is not tied to any one model.

### The four types of ambition

The essay names four types, in this order:

- **Speed:** the same work done in less time. The essay calls this the core of AI's economic value, well established and needing little creativity, and deliberately does not develop it further.
- **Altitude:** moving up in abstraction, so the model works toward the outcome rather than a single task.
- **Depth:** treating a task as a field-leading expert would, going one level below the task to its underlying data, tools and problems.
- **Range:** drawing on several fields, not only the one the task obviously belongs to, and using knowledge, tools and techniques you would not normally use.

### Altitude

A task handed to a model is the user's best guess at how to reach the outcome they want; ambition in altitude means handing over the outcome itself. The guiding question is what you want to happen next: "What's the goal beyond the goal?" The author's own example is moving from asking Claude to fix individual crashes to asking it to keep the apps crash-free.

The worked example is a quarterly business review (QBR) deck at an imagined company, Acme Inc. Merely filling in a slide template is the unambitious baseline. The essay then climbs in three steps:

1. Give the model as much of the business's data as you can, not just the template's numbers, and ask what changed this quarter, why, and what to do about it.
2. Since good meetings end in decisions, ask the model to work out the three most urgent decisions and to develop possible directions for each with arguments for and against.
3. Question the format itself: the review exists so leadership catches problems early and moves money and people to the right places. Ask the model to design a better mechanism for that than a quarterly deck, show from the company's own history that it would have caught problems sooner, and run it alongside the existing review for a quarter.

Limits and conditions the essay states for altitude:

- It works best when you really are after an ultimate outcome and less well for creative work. A good sign that it fits is that the work will be discussed in meetings.
- There are current limits: an open-ended instruction such as telling the model to go and make money does not work for most businesses on its own in 2026, although models handle higher abstraction as they become more capable.
- Altitude is where durable workflows that take the human out of the loop come from, so the user no longer feeds the model one task after another. Getting there usually means changing the workflow and environment first. For the crash-free goal, the author first had to let Claude fetch crash reports easily, map each app version to its git commit, and use Windows, macOS and Linux machines so it could reproduce and verify fixes on its own.

### Depth

Depth is for when you want a task done exceptionally well: push the model to use the tools, techniques, media and knowledge of the best professionals in the field, and keep pushing until even those experts might learn something from the result. The running example is the same QBR, assuming Acme Inc has a customer-churn problem. The essay's techniques:

- **Use the instruments the best practitioners use.** Asked to act like a professional, "models often switch vocabulary without actually switching methods". Insist on the real methods, for example databases and statistical models instead of markdown tables. The user need not know what experts use; the model usually does.
- **Set unreasonable goals and tell the model they are reasonable.** If a page must load in 5 s instead of 10 s, ask for 200 ms. If the model thinks something is impossible, tell it that it is solvable and that it needs to keep going.
- **Challenge what you know.** Many business beliefs are rough approximations. Give the model the raw data and ask it to check assumptions adversarially, for example by trying to reproduce from the raw data the belief that churn is an onboarding problem.
- **Produce new knowledge.** Once the model is deep in the data, ask it for blind spots: for example, build a simulation of the customers that reproduces the past year from the logs, find an earlier churn signal nobody knows about, and show that it predicts on data the model has not seen.
- **Use an outside judge.** "Do not ask the model to judge itself." The author expects this to be solved as models improve, but as of October 2026 he urges outside validation, ideally a tool the model can run itself for immediate feedback.

The essay closes the section with a reusable prompt that opens "I want a deeper version of this task, not a bigger one." Before rewriting a task, it asks the model to state (1) what a top professional would do that the user is not asking for, (2) the rawest material they would start from instead of already-digested material, (3) the specific methods and tools they would use, and (4) what, other than the model or the user, would show the result is right; the model then rewrites the prompt to ask for exactly that.

### Range

Range means looking at the work from the perspective of several fields, more than would have been economical before. The author compares it to heist films, which spend their opening assembling a crew with different skills. Multi-agent setups (several threads, orchestrators or subagents) make this cheaper, and he reports interesting results from asking Claude to bring in more fields. He admits it is hard and needs creativity: he had never thought of using Claude to build 3D environments for his homepage, despite having made video games, until he saw his colleague Alex Albert render interior designs in Blender. He nonetheless sees the most striking results here. Techniques:

- **Replace nouns with verbs**, a trick from *The Art of Innovation* by Tom Kelley and Jonathan Littman. The QBR is not a deck but the act of getting busy people to believe a cause-and-effect story and decide under uncertainty in 30 minutes. Stating the verb shows both user and model which fields could contribute.
- **Assemble the crew.** Imagine the deck must be extraordinary for humanity's sake and ask who would be on the team: for production quality an analyst, a journalist and an editor; for a presentation, a motion and audio designer; and as an adversarial red team, a short seller and a forensic accountant.

The essay's caveat: this easily turns into role play, which makes the transcript stranger without improving the outcome. Use the crew exercise to find fields and techniques, then have the model carry out the actual work of that role; the essay's example is to ask it not to write like a short seller but to "do what a short seller does to research their position".

### A precondition for all four types

Every kind of ambition described needs the model to have a computer on which it can install software, plus access to the relevant data, through MCP connectors or other means. The author recommends using one of the many tools that provide this.

### We have been here before

The closing section explains why the advice is needed. People are held back by what they believe possible and tend to trust themselves only in narrow disciplines; Michelangelo did not want to paint the Sistine Chapel because he saw himself as a sculptor. Psychology calls the relevant belief self-efficacy: people who believe more in their abilities achieve more. The essay argues self-efficacy can be deliberately raised, pointing to Locke and Latham's review of 35 years of goal-setting research (specific hard goals beat being told to do one's best) and to Patrick Collison's "Fast" list of achievements made under audacious goals and tight deadlines. It lists three documented ways:

- **Believing the hard thing is possible:** in 1939 George Dantzig arrived late to a Berkeley statistics class, copied two problems from the board as homework and solved them; they were unsolved problems in statistics.
- **Seeing someone else do it:** Roger Bannister broke the four-minute mile in May 1954 and was the only one to have done so for just 46 days. The essay sees the same with the two-hour marathon: Sabastian Sawe ran the first official sub-two-hour marathon in London in April 2026, and the runner-up in the same race also finished under two hours.
- **Permitting yourself to fail:** *The Inner Game of Tennis* argues that you do not play your best when trying very hard; Linux was announced as just a hobby that would not become big and professional.

The essay ends by saying self-efficacy is an old problem made more powerful now that abilities leap every few weeks, so people need techniques for doing things they had not considered or believed possible, and it invites readers to send the author further techniques. The post's image is Francisco Goya's "Modo de volar" (A Way of Flying).

## End of summary

No notes have been added beyond the summary above.
