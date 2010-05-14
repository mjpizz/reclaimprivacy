import urlparse
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


class Facebook(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'

        parts = urlparse.urlparse(self.request.url)
        if parts.port:
            bookmarklet_host = parts.hostname + ':' + str(parts.port)
        else:
            bookmarklet_host = parts.hostname
        bookmarklet_host = bookmarklet_host.replace('www.reclaimprivacy.org', 'static.reclaimprivacy.org')

        self.response.out.write('''
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
                    Drag this link to your bookmarks bar:
                    <strong>
                        <a class='bookmarklet' title="Scan for Privacy" href="javascript:(function(){var%%20script=document.createElement('script');script.src='http://%(bookmarklet_host)s/javascripts/privacyscanner.js';document.getElementsByTagName('head')[0].appendChild(script);})()">Scan for Privacy</a>
                    </strong>
                </li>
                <li>
                    Log in to <a href='http://www.facebook.com'>facebook.com</a> and then click that bookmark
                </li>
                <li>
                    You will see a series of privacy scans that inspect your privacy settings and warn you about
                    settings that might be unexpectedly public.
                </li>
            </ol>
        </p>

        <h1>Get Involved</h1>
        <p>
            Our mission is to promote privacy awareness on Facebook and elsewhere.
            Spread awareness to your friends on Facebook by sharing your
            recommendation publicly:
            <p>
                <iframe src="http://www.facebook.com/plugins/like.php?href=http%%253A%%252F%%252Fwww.reclaimprivacy.org&amp;layout=standard&amp;show_faces=false&amp;width=450&amp;action=recommend&amp;font&amp;colorscheme=dark&amp;height=35" scrolling="no" frameborder="0" style="border:none; overflow:hidden; width:450px; height:35px;" allowTransparency="true"></iframe>
            </p>
            <p>
                    <em>Are you a coder?</em> Contribute to the <a href='http://github.com/mjpizz/reclaimprivacy'>source code</a> and help to
                    keep the privacy scanner up-to-date.
            </p>
        </p>
    </div>
</body>
</html>
''' % locals())


application = webapp.WSGIApplication([
    ('/facebook', Facebook),
    ('/', Facebook),
], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()


