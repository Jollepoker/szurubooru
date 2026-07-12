<div class="nep-explanation">An image booru dedicated to Neppienep!</div>
<div class="nep-quote"><i>"Maybe I be trippin', but I never fall."</i> - 2025</div>
<ul>
    <li><%- ctx.postCount %> posts</li><span class='sep'>
    </span><li>Last build <%- ctx.isDevelopmentMode ? " (DEV MODE)" : "" %> made <%= ctx.makeRelativeTime(ctx.buildDate) %></li><span class='sep'>
    </span><% if (ctx.canListSnapshots) { %><li><a href='<%- ctx.formatClientLink('history') %>'>History</a></li><span class='sep'>
    </span><% } %>
</ul>
