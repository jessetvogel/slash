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
            // socket.send("get");
        };

        this.socket.onmessage = function (event) {
            try {
                console.info(`%c${event.data}`, 'color: gray;');
                const message = JSON.parse(event.data) as Message;
                client.handle(message);
            }
            catch (error) {
                console.error(`Failed to parse message from server!\nmessage: ${event.data}\nerror: ${error}`);
            }
        };

        this.socket.onerror = function (error) {
            console.log('WebSocket error:', error);
        };

        this.socket.onclose = function (event) {
            console.log('Connection closed.');
        };
    }

    handle(message: Message) {
        const event = message.event;

        // create
        if (event == "create") {
            const parent = $(message.parent)!;
            const tag = message.tag;

            // text
            if (tag == "text") {
                parent.append(message.text);
                return;
            }

            // html
            const id = message.id;
            const elem = create(tag, { id: id });
            parent.append(elem);
            this.update(elem, message);
            return;
        }

        // remove
        if (event == "remove") {
            const elem = $(message.id)!;
            elem.remove();
            return;
        }

        // update
        if (event == "update") {
            const elem = $(message.id)!;
            this.update(elem, message);
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
            this.functions[name](...args);
            return;
        }

        // info
        if (event == "info") {
            const info = message.info;
            console.log(`INFO: %c${info}`, 'color:rgb(71, 255, 227);');
            slash_message("info", info);
            return;
        }

        // error
        if (event == "error") {
            const error = message.error;
            console.log(`ERROR: %c${error}`, 'color: #FF474C;');
            slash_message("error", error);
            return;
        }

        // debug
        if (event == "debug") {
            const debug = message.debug;
            console.log(`DEBUG: %c${debug}`, 'color:rgb(255, 169, 71);');
            slash_message("debug", debug);
            return;
        }

        throw new Error(`Unknown event '${event}'`);
    }

    update(elem: HTMLElement, message: Message) {
        for (const attr in message) {
            if (attr == "event" || attr == "id" || attr == "parent" || attr == "tag")
                continue;

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

            elem.setAttribute(attr, message[attr])
            // throw new Error(`Unknown attribute ${attr}`)
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

let client: Client;

function init() {
    client = new Client();
    client.connect();
}

function slash_message(type: string, message: string): void {
    const div = create("div", { class: type }, message);
    setTimeout(() => div.classList.add("remove"), 5000);
    setTimeout(() => div.remove(), 5200);
    $("slash-messages")!.prepend(div);
}
