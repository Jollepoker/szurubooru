"use strict";

const api = require("../api.js");
const config = require("../config.js");
const Info = require("../models/info.js");
const topNavigation = require("../models/top_navigation.js");
const HomeView = require("../views/home_view.js");

const nepQuotes = [
    ["No matter how over it seems it can always be so back.", 2025],
    ["My mum has a salt lamp and refuses to let me lick it.", 2024],
    ["Should I get the 'straight' title guys? Nah... I'm not straight.", 2026],
    ["I want everyone to remember that you are not alone. Because Neppienep is here! :D", 2025],
    ["Your belly can never be too big! It's always not big enough!", 2026],
    ["People don't really shower every day, that's like a made up thing by the government.", 2026],
    ["A win is just a win but I wanna won!", 2026],
    ["If you're stupid it's cause your mom didn't eat enough fish.", 2026],
    ["If you don't agree with everything Neppienep says are you even really Neppienep?", 2025],
    ["Maybe I be trippin', but I never fall.", 2025],
];

class HomeController {
    constructor() {
        topNavigation.activate("home");
        topNavigation.setTitle("Home");

        const randomQuote = nepQuotes[Math.floor((Math.random()*nepQuotes.length))];

        this._homeView = new HomeView({
            name: api.getName(),
            version: config.meta.version,
            buildDate: config.meta.buildDate,
            canListSnapshots: api.hasPrivilege("snapshots:list"),
            canListPosts: api.hasPrivilege("posts:list"),
            isDevelopmentMode: config.environment == "development",
            nepQuote: randomQuote[0],
            nepQuoteYear: randomQuote[1],
        });

        Info.get().then(
            (info) => {
                this._homeView.setStats({
                    postCount: info.postCount,
                });
            },
            (error) => this._homeView.showError(error.message)
        );
    }

    showSuccess(message) {
        this._homeView.showSuccess(message);
    }

    showError(message) {
        this._homeView.showError(message);
    }
}

module.exports = (router) => {
    router.enter([], (ctx, next) => {
        ctx.controller = new HomeController();
    });
};
