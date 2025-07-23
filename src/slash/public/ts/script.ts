import { $, create } from "./utils.js";

window.addEventListener('DOMContentLoaded', init);

type Message = {
    event: string;
    [key: string]: any;
}

class Client {
    socket: WebSocket | null;
    functions: { [name: string]: Function };

    constructor() {
        this.socket = null;
        this.functions = {};

        // Cool trick
        this.onclick = this.onclick.bind(this);
        this.oninput = this.oninput.bind(this);
        this.onchange = this.onchange.bind(this);
        this.onpopstate = this.onpopstate.bind(this);

        // History event listener
        window.addEventListener("popstate", this.onpopstate);
    }

    connect() {
        // Connect to server via WebSocket
        const hostname = window.location.hostname;
        const port = window.location.port;
        this.socket = new WebSocket(`ws://${hostname}:${port}/ws`);

        console.log("Connecting to server ..");

        const client = this;

        this.socket.onopen = function () {
            console.log('Connection established!');
            client.send({
                event: "load",
                path: window.location.pathname,
                query: Object.fromEntries(new URLSearchParams(window.location.search)),
            });
        };

        const loading = $("slash-loading");

        this.socket.onmessage = async function (event) {
            loading?.remove();
            let message: Message;

            try {
                console.info(`%c${event.data}`, 'color: gray;');
                message = JSON.parse(event.data) as Message;
            }
            catch (error) {
                console.error(`Received invalid message from server\nmessage: ${event.data}`);
                Slash.message(
                    'error',
                    `<b>Received invalid message from server</b><pre><code>${event.data}</code></pre><span>${error}</span>`,
                    { format: "html" }
                );
                return;
            }

            try {
                await client.handle(message);
            }
            catch (error) {
                Slash.message(
                    'error',
                    `<b>Failed to handle message from server</b><pre><code>${event.data}</code></pre><span>${error}</span>`,
                    { format: "html" }
                );
                return;
            }
        };

        this.socket.onerror = function (error) {
            console.log('WebSocket error:', error);
        };

        this.socket.onclose = function () {
            console.log('Connection closed.');
            Slash.message('warning', 'Connection lost! Try reloading the page to reconnect to the server.', { permanent: true });
        };
    }

    async handle(message: Message) {
        const event = message.event;

        // create
        if (event == "create") {
            const tag = message.tag;

            // text
            if (tag === undefined) {
                const parent = this.getElementById(message.parent);
                parent.append(message.text);
                return;
            }

            // html
            const elem = (message.ns !== undefined)
                ? document.createElementNS(message.ns, tag)
                : document.createElement(tag);
            elem.id = message.id;
            this.update(elem, message);
            return;
        }

        // update
        if (event == "update") {
            const elem = this.getElementById(message.id);
            this.update(elem, message);
            return;
        }

        // remove
        if (event == "remove") {
            const elem = this.getElementById(message.id);
            elem.remove();
            return;
        }

        // clear
        if (event == "clear") {
            const elem = this.getElementById(message.id);
            elem.innerHTML = "";
            return;
        }

        // html
        if (event == "html") {
            const elem = this.getElementById(message.id);
            elem.innerHTML = message.html;
            return;
        }

        // script
        if (event == "script") {
            const script = message.script;
            eval?.(`"use strict";(${script})`);
            return;
        }

        // function
        if (event == "function") {
            const name = message.name;
            const args = message.args;
            const body = message.body;
            this.functions[name] = new Function(...args, body);
            return;
        }

        // execute
        if (event == "execute") {
            const name = message.name;
            const args = message.args;
            const value = this.functions[name](...args);
            if (message.store)
                Slash.store(message.store, value);
            return;
        }

        // log
        if (event == "log") {
            const type = message.type;
            const text = message.message;
            const format = message.format || "text";
            console.log(`[${type}] %c${text}`, 'color:rgb(216, 198, 162);');
            Slash.message(type, text, { format: format });
            return;
        }

        // theme
        if (event == "theme") {
            const theme = message.theme;
            document.body.className = theme;
            window.localStorage.setItem("SLASH_THEME", theme);
            return;
        }

        // title
        if (event == "title") {
            document.title = message.title;
            return;
        }

        // cookie
        if (event == "cookie") {
            const name = message.name;
            const value = message.value;
            const days = message.days;
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            const expires = "expires=" + date.toUTCString();
            document.cookie = name + "=" + value + ";" + expires + ";path=/";;
            return;
        }

        // history
        if (event == "history") {
            if ("go" in message) {
                window.history.go(message.go);
                return;
            }
            if ("push" in message) {
                window.history.pushState(message.push, "", message.url);
                return;
            }
            if ("replace" in message) {
                window.history.replaceState(message.replace, "", message.url);
                return;
            }
            throw new Error("Invalid history event: missing field `go`, `push` or `replace`.");
        }

        throw new Error(`Unknown event '${event}'`);
    }

    update(elem: HTMLElement, message: Message) {
        for (const attr in message) {
            if (attr == "event" || attr == "id" || attr == "tag" || attr == "ns" || attr == "position")
                continue;

            if (attr == "parent") {
                const parent = this.getElementById(message.parent);
                if ("position" in message) {
                    if (Object.values(parent.children).includes(elem))
                        parent.removeChild(elem);
                    const position = message.position;

                    if (position >= parent.children.length) {
                        parent.append(elem);
                    } else {
                        parent.insertBefore(elem, parent.children[position]);
                    }
                }
                else {
                    parent.append(elem);
                }
                continue;
            }

            if (attr == "style") {
                for (const [key, value] of Object.entries(message.style)) {
                    if (value !== null && typeof value !== 'string')
                        throw new Error(`Invalid value for style property ${key}`);
                    elem.style.setProperty(key, value);
                }
                continue;
            }

            if (attr == "onclick") {
                if (message.onclick === true) {
                    elem.addEventListener("click", this.onclick);
                } else {
                    elem.removeEventListener("click", this.onclick);
                }
                continue;
            }

            if (attr == "oninput") {
                if (message.oninput === true) {
                    elem.addEventListener('input', this.oninput);
                } else {
                    elem.removeEventListener("input", this.oninput);
                }
                continue;
            }

            if (attr == "onchange") {
                if (message.onchange === true) {
                    elem.addEventListener('change', this.onchange);
                } else {
                    elem.removeEventListener("change", this.onchange);
                }
                continue;
            }

            if (attr == "text") {
                elem.innerText = message.text;
                continue;
            }

            if (attr == "value") {
                if ('value' in elem) {
                    elem.value = message.value;
                    continue;
                }
            }

            const value = message[attr];
            if (value === null) // null means to remove the attribute
                elem.removeAttribute(attr);
            else
                elem.setAttribute(attr, value);
        }
    }

    onclick(event: MouseEvent) {
        const elem = event.currentTarget;
        if (elem instanceof HTMLElement) {
            this.send({
                event: "click",
                id: elem.id
            });
            event.stopPropagation();
        }
    }

    oninput(event: Event) {
        const elem = event.currentTarget;
        if (elem !== null && "id" in elem && "value" in elem) {
            this.send({
                event: "input",
                id: elem.id,
                value: elem.value
            });
        }
    }

    onchange(event: Event) {
        const elem = event.currentTarget;
        if (elem !== null && "id" in elem && "value" in elem) {
            this.send({
                event: "change",
                id: elem.id,
                value: elem.value
            });
        }
    }

    onpopstate(event: PopStateEvent) {
        this.send({
            event: "popstate",
            state: event.state
            // TODO: location info
        })
    }

    send(message: Message) {
        this.socket?.send(JSON.stringify(message));
    }

    getElementById(id: string): HTMLElement {
        const elem = $(id);
        if (elem == null)
            throw new Error(`No element exists with id '${id}'`);
        return elem;
    }
}

class Slash {

    static values: { [name: string]: any } = {};

    static store(name: string, value: any): void {
        Slash.values[name] = value;
    }

    static value(name: string): any {
        return Slash.values[name];
    }

    static message(type: string, message: string, options: { timeout?: number, format?: string, permanent?: boolean } = {}): void {
        const div = create("div", { class: "message " + type }, create("span", { class: "icon" }));

        if (options.format == "html")
            div.insertAdjacentHTML('beforeend', message);
        else
            div.append(message);

        if (options.permanent !== true) {
            const timeout = options.timeout || 10_000; // 10 sec
            setTimeout(() => div.classList.add("remove"), timeout);
            setTimeout(() => div.remove(), timeout + 500);
        }

        $("slash-messages")!.prepend(div);
    }
}

let client: Client;

function init() {
    (window as any).Slash = Slash;
    Slash.message("warning", "", { timeout: -499 }); // preload the warning icon

    const theme = window.localStorage.getItem("SLASH_THEME");
    if (theme !== null) document.body.className = theme;

    client = new Client();
    client.connect();
}
