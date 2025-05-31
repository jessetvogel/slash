import { $, create } from "./utils.js";
window.addEventListener('DOMContentLoaded', init);
class Client {
    constructor() {
        this.socket = null;
        this.functions = {};
        this.onclick = this.onclick.bind(this);
        this.oninput = this.oninput.bind(this);
        this.onchange = this.onchange.bind(this);
    }
    connect() {
        const hostname = window.location.hostname;
        const port = window.location.port;
        this.socket = new WebSocket(`ws://${hostname}:${port}/ws`);
        console.log("Connecting to server ..");
        const client = this;
        this.socket.onopen = function (event) {
            console.log('Connection established!');
        };
        this.socket.onmessage = function (event) {
            try {
                console.info(`%c${event.data}`, 'color: gray;');
                const message = JSON.parse(event.data);
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
    handle(message) {
        const event = message.event;
        if (event == "create") {
            const parent = $(message.parent);
            const tag = message.tag;
            if (tag == "text") {
                parent.append(message.text);
                return;
            }
            const id = message.id;
            const elem = create(tag, { id: id });
            parent.append(elem);
            this.update(elem, message);
            return;
        }
        if (event == "remove") {
            const elem = $(message.id);
            elem.remove();
            return;
        }
        if (event == "update") {
            const elem = $(message.id);
            this.update(elem, message);
            return;
        }
        if (event == "script") {
            const script = message.script;
            eval === null || eval === void 0 ? void 0 : eval(`"use strict";(${script})`);
            return;
        }
        if (event == "function") {
            const name = message.name;
            const args = message.args;
            const body = message.body;
            this.functions[name] = new Function(...args, body);
            return;
        }
        if (event == "execute") {
            const name = message.name;
            const args = message.args;
            this.functions[name](...args);
            return;
        }
        if (event == "info") {
            const info = message.info;
            console.log(`INFO: %c${info}`, 'color:rgb(71, 255, 227);');
            slash_message("info", info);
            return;
        }
        if (event == "debug") {
            const debug = message.debug;
            console.log(`DEBUG: %c${debug}`, 'color:rgb(104, 167, 77);');
            slash_message("debug", debug);
            return;
        }
        if (event == "warning") {
            const warning = message.warning;
            console.log(`WARNING: %c${warning}`, 'color:rgb(255, 169, 71);');
            slash_message("warning", warning);
            return;
        }
        if (event == "error") {
            const error = message.error;
            console.log(`ERROR: %c${error}`, 'color: #FF474C;');
            slash_message("error", error);
            return;
        }
        throw new Error(`Unknown event '${event}'`);
    }
    update(elem, message) {
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
                }
                else {
                    elem.removeEventListener("click", this.onclick);
                }
                continue;
            }
            if (attr == "oninput") {
                if (message.oninput === true) {
                    elem.addEventListener('input', this.oninput);
                }
                else {
                    elem.removeEventListener("input", this.oninput);
                }
                continue;
            }
            if (attr == "onchange") {
                if (message.onchange === true) {
                    elem.addEventListener('change', this.onchange);
                }
                else {
                    elem.removeEventListener("change", this.onchange);
                }
                continue;
            }
            if (attr == "text") {
                elem.innerText = message.text;
                continue;
            }
            elem.setAttribute(attr, message[attr]);
        }
    }
    onclick(event) {
        const elem = event.currentTarget;
        if (elem instanceof HTMLElement) {
            this.send({
                event: "click",
                id: elem.id
            });
            event.stopPropagation();
        }
    }
    oninput(event) {
        const elem = event.currentTarget;
        if (elem !== null && "id" in elem && "value" in elem) {
            this.send({
                event: "input",
                id: elem.id,
                value: elem.value
            });
        }
    }
    onchange(event) {
        const elem = event.currentTarget;
        if (elem !== null && "id" in elem && "value" in elem) {
            this.send({
                event: "change",
                id: elem.id,
                value: elem.value
            });
        }
    }
    send(message) {
        var _a;
        (_a = this.socket) === null || _a === void 0 ? void 0 : _a.send(JSON.stringify(message));
    }
}
;
let client;
function init() {
    client = new Client();
    client.connect();
}
function slash_message(type, message) {
    const div = create("div", { class: "message " + type }, [
        create("span", { class: "icon" }),
        create("span", {}, message)
    ]);
    setTimeout(() => div.classList.add("remove"), 5000);
    setTimeout(() => div.remove(), 5200);
    $("slash-messages").prepend(div);
}
