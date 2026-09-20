"use strict";

const router = require("../router.js");
const uri = require("../util/uri.js");
const misc = require("../util/misc.js");
const views = require("../util/views.js");
const PostContentControl = require("../controls/post_content_control.js");
const PostNotesOverlayControl = require("../controls/post_notes_overlay_control.js");
const TagAutoCompleteControl = require("../controls/tag_auto_complete_control.js");

const template = views.getTemplate("home");
const footerTemplate = views.getTemplate("home-footer");

class HomeView {
    constructor(ctx) {
        this._hostNode = document.getElementById("content-holder");
        this._ctx = ctx;

        const sourceNode = template(ctx);
        views.replaceContent(this._hostNode, sourceNode);
        views.syncScrollPosition();

        if (this._formNode) {
            this._autoCompleteControl = new TagAutoCompleteControl(
                this._searchInputNode,
                {
                    confirm: (tag) =>
                        this._autoCompleteControl.replaceSelectedText(
                            misc.escapeSearchTerm(tag.matchingNames[0]),
                            true
                        ),
                    isNegationAllowed: true,
                }
            );
            this._formNode.addEventListener("submit", (e) =>
                this._evtFormSubmit(e)
            );
        }
    }

    showSuccess(text) {
        views.showSuccess(this._hostNode, text);
    }

    showError(text) {
        views.showError(this._hostNode, text);
    }

    setStats(stats) {
        views.replaceContent(
            this._footerContainerNode,
            footerTemplate(Object.assign({}, stats, this._ctx))
        );
    }

    get _footerContainerNode() {
        return this._hostNode.querySelector(".footer-container");
    }

    get _nepBannerContainerNode() {
        return this._hostNode.querySelector(".nep-banner-container");
    }

    get _postContainerNode() {
        return this._hostNode.querySelector(".post-container");
    }

    get _formNode() {
        return this._hostNode.querySelector("form");
    }

    get _searchInputNode() {
        return this._formNode.querySelector("input[name=search-text]");
    }

    _evtFormSubmit(e) {
        e.preventDefault();
        this._searchInputNode.blur();
        router.show(
            uri.formatClientLink("posts", {
                query: this._searchInputNode.value,
            })
        );
    }
}

module.exports = HomeView;
