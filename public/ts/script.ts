import { $, create } from "./utils.js";

window.addEventListener('DOMContentLoaded', init);

type Message = {
    event: string;
    [key: string]: any;
};

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
    }

    connect() {
        // Connect to server via WebSocket
        const hostname = window.location.hostname;
        const port = window.location.port;
        this.socket = new WebSocket(`ws://${hostname}:${port}/ws`)

        console.log("Connecting to server ..");

        const client = this;

        this.socket.onopen = function (event) {
            console.log('Connection established!');
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
                Slash.message('error', `<span>Received invalid message from server</span><pre><code>${event.data}</code></pre><span>${error}</span>`);
                return;
            }

            try {
                await client.handle(message);
            }
            catch (error) {
                Slash.message('error', `<span>Failed to handle message from server</span><pre><code>${event.data}</code></pre><span>${error}</span>`);
                return;
            }
        };

        this.socket.onerror = function (error) {
            console.log('WebSocket error:', error);
        };

        this.socket.onclose = function (event) {
            console.log('Connection closed.');
            Slash.message('warning', 'Connection lost');
        };
    }

    async handle(message: Message) {
        const event = message.event;

        // create
        if (event == "create") {
            const tag = message.tag;

            // text
            if (tag === undefined) {
                $(message.parent)!.append(message.text);
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
            const elem = $(message.id);
            if (elem == null) throw new Error(`No element exists with id '${message.id}'`);
            this.update(elem, message);
            return;
        }

        // remove
        if (event == "remove") {
            const elem = $(message.id);
            if (elem == null) throw new Error(`No element exists with id '${message.id}'`);
            elem.remove();
            return;
        }

        // clear
        if (event == "clear") {
            const elem = $(message.id);
            if (elem == null) throw new Error(`No element exists with id '${message.id}'`);
            elem.innerHTML = "";
            return;
        }

        // html
        if (event == "html") {
            const elem = $(message.id);
            if (elem == null) throw new Error(`No element exists with id '${message.id}'`);
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
            console.log(`[${type}] %c${text}`, 'color:rgb(216, 198, 162);');
            Slash.message(type, text);
            return;
        }

        throw new Error(`Unknown event '${event}'`);
    }

    update(elem: HTMLElement, message: Message) {
        for (const attr in message) {
            if (attr == "event" || attr == "id" || attr == "tag" || attr == "ns")
                continue;

            if (attr == "parent") {
                const parent = $(message.parent);
                if (parent === null) throw new Error(`No element exists with id '${message.parent}'`);
                parent.append(elem);
                continue;
            }

            if (attr == "style") {
                for (const [key, value] of Object.entries(message.style)) {
                    if (typeof value !== 'string')
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

    send(message: Message) {
        this.socket?.send(JSON.stringify(message));
    }
};

class Slash {

    static values: { [name: string]: any } = {};

    static store(name: string, value: any): void {
        Slash.values[name] = value;
    }

    static value(name: string): any {
        return Slash.values[name];
    }

    static message(type: string, message: string): void {
        const div = create("div", { class: "message " + type }, [
            create("span", { class: "icon" }),
            message
        ]);
        const timeout = 10000;
        setTimeout(() => div.classList.add("remove"), timeout);
        setTimeout(() => div.remove(), timeout + 500);
        $("slash-messages")!.prepend(div);
    }
};

let client: Client;

function init() {
    (window as any).Slash = Slash;

    client = new Client();
    client.connect();
}
