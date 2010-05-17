import os
import urlparse
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

VERSION = '4'


class Facebook(webapp.RequestHandler):
    def get(self):
        # detect MSIE
        if 'MSIE' in os.environ['HTTP_USER_AGENT']:
            is_iebrowser = 1
        else:
            is_iebrowser = 0

        # build the memcache key we will use
        version = VERSION
        memcache_key = 'page_content:%(version)s:%(is_iebrowser)s' % locals()

        # try to get a cached page, and otherwise build the page
        page_content = memcache.get(memcache_key)
        if not page_content:

            # figure out the host name of this server (for serving the proper
            # javascript bookmarklet)
            parts = urlparse.urlparse(self.request.url)
            if parts.port:
                bookmarklet_host = parts.hostname + ':' + str(parts.port)
            else:
                bookmarklet_host = parts.hostname

            # we need to serve a different bookmarklet Javascript for MSIE
            if is_iebrowser:
                step_one_instructions = "Right-click this link and 'Add to Favorites'"
                step_two_instructions = "Log in to <a href='http://www.facebook.com'>facebook.com</a>, open your Favorites, and click the link called 'Scan for Privacy'"
            else:
                step_one_instructions = "Drag this link to your web browser bookmarks bar"
                step_two_instructions = "Log in to <a href='http://www.facebook.com'>facebook.com</a> and then click that bookmark"

            # build the page HTML
            bookmarklet_host = bookmarklet_host.replace('www.reclaimprivacy.org', 'static.reclaimprivacy.org')
            page_content = '''
<html>
<head>
    <title>ReclaimPrivacy.org | Facebook Privacy Scanner</title>
    <link rel="stylesheet" href="/stylesheets/main.css" type="text/css" media="screen" title="no title" charset="utf-8">
    
</head>
<body>

    <div id='logo'>
        <a href="http://www.reclaimprivacy.org"><img src='/images/logo.png' /></a>
        <div>
            <strong>ReclaimPrivacy</strong><span class='soft'>.org</span>
        </div>
    </div>

    <div id='content'>
        <h1>Get Informed</h1>
        <p>
            Keep up with the latest news about privacy policies on Facebook.
            <ul>
                <li>
                    <a href='http://www.eff.org/deeplinks/2010/04/facebook-further-reduces-control-over-personal-information'>The Erosion of Facebook Privacy</a>
                    <span class='soft'>eff.org</span>
                </li>
                <li>
                    <a href='http://www.eff.org/deeplinks/2009/12/facebooks-new-privacy-changes-good-bad-and-ugly'>Facebook Privacy Changes</a>
                    <span class='soft'>eff.org</span>
                </li>
                <li>
                    <a href='http://finance.yahoo.com/family-home/article/109538/7-things-to-stop-doing-now-on-facebook'>7 Things to Stop Doing Now on Facebook</a>
                    <span class='soft'>yahoo.com</span>
                </li>
                <li>
                    <a href='http://www.wired.com/epicenter/2010/05/facebook-rogue/'>Facebook's Gone Rogue</a>
                    <span class='soft'>wired.com</span>
                </li>
            </ul>
        </p>

        <h1>Get Protected</h1>
        <p>
            This website provides an <strong>independent</strong> and <strong>open</strong> tool for scanning
            your Facebook privacy settings.  <em>The <a href='http://github.com/mjpizz/reclaimprivacy'>source code</a> and its development will always remain open and transparent.</em>
            <ol>
                <li>
                    %(step_one_instructions)s:
                    <strong>
                        <a class='bookmarklet' title="Scan for Privacy" href="javascript:(function(){var%%20script=document.createElement('script');script.src='http://%(bookmarklet_host)s/javascripts/privacyscanner.js';document.getElementsByTagName('head')[0].appendChild(script);})()">Scan for Privacy</a>
                    </strong>
                </li>
                <li>
                    %(step_two_instructions)s
                </li>
                <li>
                    You will see a series of privacy scans that inspect your privacy settings and warn you about
                    settings that might be unexpectedly public.
                </li>
                <li>
                    <a href="http://www.facebook.com/pages/Reclaim-Privacy/121897834504447">Follow us on Facebook</a>
                    to hear about the latest updates.
                </li>
            </ol>
        </p>

        <h1>Get Involved</h1>
        <p>
            Our mission is to promote privacy awareness on Facebook and elsewhere.
            Spread awareness to your friends on Facebook by sharing this website with them:
            <p>
                <a name="fb_share" type="button_count" share_url="http://www.reclaimprivacy.org/facebook" href="http://www.facebook.com/sharer.php">Share</a><script src="http://static.ak.fbcdn.net/connect.php/js/FB.Share" type="text/javascript"></script>
            </p>
            <p>
                    <em>Are you a coder?</em> Contribute to the <a href='http://github.com/mjpizz/reclaimprivacy'>source code</a> and help to
                    keep the privacy scanner up-to-date.
            </p>
        </p>

        <h1>Read Our Own Privacy Policy</h1>
        <p>
            Our privacy policy is not long:
            <ul>
                <li>we <strong>never see</strong> your Facebook data</li>
                <li>we <strong>never share</strong> your personal information</li>
            </ul>
            Simple.  The scanner operates entirely within your own browser.
        </p>
        <p>
            <em>Statement of limitation of liability:</em>
            <strong>you use this tool at your own risk</strong>, and by using this tool you agree
            to hold neither ReclaimPrivacy.org (nor its contributors) liable for
            damage to your Facebook account.
            <strong>However, we do strive to reduce that risk
            by keeping the source code open and transparent</strong>, so that
            we can identify bugs and quickly fix any functionality.
        </p>
    </div>

<!-- begin olark code -->
<script type='text/javascript'>
(function(d,u){var h=d.location.protocol=='https:'?'https://':'http://';d.write(
unescape("%%3Cscript src='"+h+u+"' type='text/javascript'%%3E%%3C/script%%3E"));
})(document,'static.olark.com/javascript/olark.js');
</script>
<a href='http://olark.com/about' id='olark-key' class='site-9122-608-10-8698' style='display:none' rel='nofollow'>
Powered by Olark
</a>
<!-- end olark code-->

<script type='text/javascript'>
olark.extend(function(api){
    api.chat.updateVisitorNickname({snippet: 'reclaimprivacy'})
});
</script>

</body>
</html>
            ''' % locals()

            # cache the page in memcache
            memcache.set(memcache_key, page_content)

        # write the response
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(page_content)


application = webapp.WSGIApplication([
    ('/facebook', Facebook),
    ('/', Facebook),
], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()


