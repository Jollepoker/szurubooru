<div class='content-wrapper transparent' id='home'>
    <div class='messages'></div>
    <header>
        <h1><%- ctx.name %></h1>
    </header>
    <% if (ctx.canListPosts) { %>
        <form>
            <div class="inputs">
                <%= ctx.makeTextInput({name: 'search-text', placeholder: 'Ex: neppienep'}) %>
                <input type='submit' value='Search'/>
            </div>
            <a href='<%- ctx.formatClientLink('posts') %>'>Browse All Posts</a>
        </form>
    <% } %>
    <div class='nep-banner-container'>
        <div class='nep-image-container'>
            <img src="img/neptest.png" />
        </div>
    </div>
    <footer class='footer-container'></footer>
</div>
