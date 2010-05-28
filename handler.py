import os
import logging
import urlparse
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

VERSION = '55'


class NewsletterEntry(db.Model):
    email_address = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)


class DesktopAppEntry(db.Model):
    email_address = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)


class Newsletter(webapp.RequestHandler):
    def get(self):
        email = self.request.get('email')
        if email:
            try:
                num_previous_entries = NewsletterEntry.gql('WHERE email_address = :1 LIMIT 1', email).count()
                if num_previous_entries != 0:
                    logging.error("already have email address: %(email)s" % locals())
                else:
                    entry = NewsletterEntry()
                    entry.email_address = email
                    entry.put()
            except Exception, e:
                logging.error('error adding email: ', e)
        else:
            logging.error('email not given')
        self.redirect('/')


class DesktopApp(webapp.RequestHandler):
    def get(self):
        email = self.request.get('email')
        if email:
            try:
                num_previous_entries = DesktopAppEntry.gql('WHERE email_address = :1 LIMIT 1', email).count()
                if num_previous_entries != 0:
                    logging.error("already have email address: %(email)s" % locals())
                else:
                    entry = DesktopAppEntry()
                    entry.email_address = email
                    entry.put()
            except Exception, e:
                logging.error('error adding email: ', e)
        else:
            logging.error('email not given')
        self.redirect('/help')


class Facebook(webapp.RequestHandler):
    def get(self):
        # detect MSIE
        if 'MSIE' in os.environ['HTTP_USER_AGENT'] and 'irefox' not in os.environ['HTTP_USER_AGENT']:
            browser = 'msie'
        elif 'Opera' in os.environ['HTTP_USER_AGENT']:
            browser = 'opera'
        else:
            browser = 'other'

        # build the memcache key we will use
        version = VERSION
        memcache_key = 'page_content:facebook:%(version)s:%(browser)s' % locals()

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
            if browser == 'ie':
                step_one_instructions = "Right-click this grey button and 'Add to Favorites'"
                step_two_instructions = "<a href='http://www.facebook.com/settings/?tab=privacy&ref=mb' target='_blank'>Go to your Facebook privacy settings</a>, open your Favorites, and click the link called 'Scan for Privacy' once you are on Facebook"
            elif browser == 'opera':
                step_one_instructions = "Hold down the Shift key, then <strong>drag</strong> this grey button to your browser toolbar"
                step_two_instructions = "<a href='http://www.facebook.com/settings/?tab=privacy&ref=mb' target='_blank'>Go to your Facebook privacy settings</a>, open your Favorites, and click the link called 'Scan for Privacy' once you are on Facebook"
            else:
                step_one_instructions = "Drag this grey button to your browser bookmarks bar"
                step_two_instructions = "<a href='http://www.facebook.com/settings/?tab=privacy&ref=mb' target='_blank'>Go to your Facebook privacy settings</a> and then click that bookmark once you are on Facebook."

            # build the page HTML
            leftbar_content = _get_leftbar_content()
            bookmarklet_host = bookmarklet_host.replace('www.reclaimprivacy.org', 'static.reclaimprivacy.org')
            page_content = '''
<html>
<head>
    <title>ReclaimPrivacy.org | Facebook Privacy Scanner</title>
    <link rel="stylesheet" href="/stylesheets/main.css" type="text/css" media="screen" title="no title" charset="utf-8">
    
</head>
<body>

    <div id='logo'>
        %(leftbar_content)s
    </div>

    <div id='content'>

        <h1>Get Protected</h1>
        <p>
            This website provides an <strong>independent</strong> and <strong>open</strong> tool for scanning
            your Facebook privacy settings.
            <div class='fresh-banner'>
                <span class='label'>new!</span>
                just added Photo Album privacy scanning
            </div>
            <ol class='instructions'>
                <li>
                    %(step_one_instructions)s:
                    <strong>
                        <a class='bookmarklet' title="Scan for Privacy" href="javascript:(function(){var%%20script=document.createElement('script');script.src='http://%(bookmarklet_host)s/javascripts/privacyscanner.js';document.getElementsByTagName('head')[0].appendChild(script);})()">Scan for Privacy<span class='helper-arrow arrow-on-%(browser)s'></span></a>
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
                <li>
                    Tell your friends to check their privacy too: <a name="fb_share" type="button_count" share_url="http://www.reclaimprivacy.org/facebook" href="http://www.facebook.com/sharer.php">Share</a><script src="http://static.ak.fbcdn.net/connect.php/js/FB.Share" type="text/javascript"></script>
                </li>
            </ol>
            <p class='need-help'>
                <em>
                    Having trouble? <a href='/help'>Check our help page</a> for tips and video walkthroughs.
                </em>
            </p
        </p>

        <h1>Get Involved</h1>
        <p>
            Our mission is to promote privacy awareness on Facebook and elsewhere.
            Spread awareness to your friends on Facebook by sharing this website with them:
            <p>
                <a name="fb_share" type="button_count" share_url="http://www.reclaimprivacy.org/facebook" href="http://www.facebook.com/sharer.php">Share</a><script src="http://static.ak.fbcdn.net/connect.php/js/FB.Share" type="text/javascript"></script>
            </p>
            <p>
                You can <a href='http://twitter.com/reclaimprivacy'>follow us on Twitter</a> too!
            </p>
            <p>
                <form class='newsletter' action='/newsletter'>
                    <div class='message'>
                        If you prefer email, you can also sign up for the newsletter to get informed of privacy updates:
                    </div>
                    <label for='email'>email:</label>
                    <input type='text' name='email' />
                    <input type='submit' value='sign me up for the newsletter' />
                </form>
            </p>
            <p>
                    Are you a programmer? <a href='http://github.com/mjpizz/reclaimprivacy'>Contribute to the source code</a> and help to
                    keep the privacy scanner up-to-date.  All development will remain open and transparent.
            </p>
        </p>

        <h1>Stay Informed</h1>
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

        <h1>Read Our Own Privacy Policy</h1>
        <p>
            Our privacy policy is not long:
            <ul>
                <li>we <strong>never see</strong> your Facebook data</li>
                <li>we <strong>never share</strong> your personal information</li>
            </ul>
            Simple.  After the scanner is downloaded from reclaimprivacy.org, it operates entirely
            between your own browser and Facebook.
        </p>

        <h1>Be Security Conscious</h1>
        <p>
            Please <strong>be safe</strong>.  Make sure you know that a link (like this)
            or application (like those on Facebook) is <strong>trustworthy</strong> before
            you install it.  <strong>We try to ensure a measure of accountability</strong> for our own link
            by releasing all of our code (including this website itself) as open-source, and maintaining
            good communication about important updates.
        </p>
        <p>
            You should <strong>never</strong> use this scanner on a secure
            website like your bank or any other financial institution.  Keep
            in mind that those websites often have far more sensitive information than Facebook.
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

        <div class='about-section'>
            <h2>about the community contributors</h2>
            <p>
                Frieder contributed the German translation of the tool.  <a href='http://www.bitwig.com'>Pablo</a> contributed the snazzy new logo.
                <a href='http://github.com/leighman'>@leighman</a> contributed usability improvements to the website.
                <a href='http://github.com/zkwentz'>@zkwentz</a> contributed status update privacy scans.
                Matteo and <a href='http://github.com/mfornasa'>@mfornasa</a> both provided Italian translations of the tool.
                Renaud provided the French translations of the tool.
            </p>
            <h2>about the original author</h2>
            <p>
                I am an avid Javascript developer and co-founder at <a href='http://www.olark.com/'>Olark</a> (check it out!).  You
                can chat with me about ReclaimPrivacy.org on the <a href='/help'>help page</a>.  If you're with the press, please use
                press@reclaimprivacy.org to reach us.
            </p>
        </div>
    </div>

</body>
</html>
            ''' % locals()

            # cache the page in memcache (only on the production servers)
            if 'reclaimprivacy.org' in parts.hostname:
                memcache.set(memcache_key, page_content)

        # write the response
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(page_content)


class Help(webapp.RequestHandler):
    def get(self):
        # detect MSIE
        if 'MSIE' in os.environ['HTTP_USER_AGENT'] and 'irefox' not in os.environ['HTTP_USER_AGENT']:
            browser = 'msie'
        elif 'Opera' in os.environ['HTTP_USER_AGENT']:
            browser = 'opera'
        else:
            browser = 'other'

        # build the memcache key we will use
        version = VERSION
        memcache_key = 'page_content:help:%(version)s' % locals()

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

            # render the page
            leftbar_content = _get_leftbar_content()
            page_content = '''
<html>
<head>
    <title>ReclaimPrivacy.org | Facebook Privacy Scanner</title>
    <link rel="stylesheet" href="/stylesheets/main.css" type="text/css" media="screen" title="no title" charset="utf-8">

</head>
<body>

    <div id='logo'>
        %(leftbar_content)s
    </div>

    <div id='content'>

        <h1>Frequently Asked Questions</h1>

        <p>
            <em>Here are some of the questions that many people like you have asked...</em>
        </p>
        <p>
            <h3>How do I add the "Scan for Privacy" bookmark?</h3>
            <p class='answer'>
                You can either <strong>drag</strong> it to your bookmarks bar or <strong>right click it</strong> and
                add it to your bookmarks/favorites.
            </p>
            <p class='answer'>
                <em class='soft'>this grey box is the bookmark:</em>
                <strong>
                    <a class='bookmarklet' title="Scan for Privacy" href="javascript:(function(){var%%20script=document.createElement('script');script.src='http://%(bookmarklet_host)s/javascripts/privacyscanner.js';document.getElementsByTagName('head')[0].appendChild(script);})()">Scan for Privacy<span class='helper-arrow arrow-on-%(browser)s'></span></a>
                </strong>
            </p>
            <p class='answer'>
                <strong>After you have added that grey box bookmark</strong> you need to
                <a href='http://www.facebook.com/settings/?tab=privacy&ref=mb' target='_blank'>go to your Facebook privacy settings</a>.
                <strong>Once you are on Facebook</strong>, you should click that bookmark.
            </p>
        </p>
        <p>
            <h3>I can't drag the "Scan for Privacy" bookmark, what can I do?</h3>
            <p class='answer'>
                <strong>If you are using Safari or Chrome</strong>: click "View...Show Bookmarks Bar", and then you will be able to drag the link into it.
            </p>
            <p class='answer'>
                <strong>If you are using Internet Explorer</strong>: right-click the grey bookmark button, and click "Add to Favorites".
            </p>
            <p class='answer'>
                <strong>If you are using Opera</strong>: make sure you hold down the Shift key before you start dragging.
            </p>
        </p>
        <p>
            <h3>Why does the bookmark take me back to ReclaimPrivacy.org?</h3>
            <p class='answer'>
                You probably bookmarked the homepage, instead of bookmarking the
                grey "Scan for Privacy" button. Make sure that you bookmark (or favorite) the grey button,
                instead of the page.
            </p>
            <p class='answer'>
                <em class='soft'>this grey box is the bookmark:</em>
                <strong>
                    <a class='bookmarklet' title="Scan for Privacy" href="javascript:(function(){var%%20script=document.createElement('script');script.src='http://%(bookmarklet_host)s/javascripts/privacyscanner.js';document.getElementsByTagName('head')[0].appendChild(script);})()">Scan for Privacy<span class='helper-arrow arrow-on-%(browser)s'></span></a>
                </strong>
            </p>
        </p>
        <p>
            <h3>Some of the settings never get fixed, what can I do?</h3>
            <p class='answer'>
                Sometimes the automatic fixes have trouble working, but the scan
                will <strong>always have a link</strong> to the right page in your privacy settings.  That
                way you can always go and fix that privacy setting yourself, even
                when the scanner cannot automatically fix it.
            </p>
        </p>
        <p>
            <h3>Why is the scanner stuck on the 4th and 6th lines?</h3>
            <p class='answer'>
                We are currently working on fixing <a href='http://github.com/mjpizz/reclaimprivacy/issues#issue/2'>this bug</a> (if you are a programmer
                and can help, let me know).  The easiest thing to do in the
                meantime is to use Chrome, Internet Explorer, or Safari (those browsers work a bit better).
            </p>
        </p>

        <h1>Video Walkthroughs</h1>
        <p>
            If you are having trouble setting up the privacy scanner, watch the video
            walkthrough for your browser.
            <ul class='browser-walkthrough'>
                <li class='enabled for-windows'>
                    <a href='http://www.youtube.com/watch?v=lVQga-m4aRk' title='Google Chrome Privacy Walkthrough Video' target='_blank'>
                        <img src='/images/google-chrome-logo.png' width='90' height='87' /><span class='label'>Chrome (Windows)</span>
                        <span class='volunteers-needed'>volunteers needed!</span>
                    </a>
                </li>
                <li class='enabled for-mac'>
                    <a href='http://www.youtube.com/watch?v=lVQga-m4aRk' title='Google Chrome Privacy Walkthrough Video' target='_blank'>
                        <img src='/images/google-chrome-logo.png' width='90' height='87' /><span class='label'>Chrome (Mac)</span>
                        <span class='volunteers-needed'>volunteers needed!</span>
                    </a>
                </li>
                <li class='enabled for-mac'>
                    <a href='http://www.youtube.com/watch?v=BsTF8vbi3ns' title='Safari Privacy Walkthrough Video' target='_blank'>
                        <img src='/images/safari-logo.png' width='90' height='90' /><span class='label'>Safari</span>
                        <span class='volunteers-needed'>volunteers needed!</span>
                    </a>
                </li>
                <li class='disabled for-windows'>
                    <a href='#' title='Internet Explorer Privacy Walkthrough Video' onclick='return false;'>
                        <img src='/images/ie-logo.png' width='90' height='90' /><span class='label'>Internet Explorer</span>
                        <span class='volunteers-needed'>volunteers needed!</span>
                    </a>
                </li>
                <li class='enabled for-mac'>
                    <a href='http://www.youtube.com/watch?v=u105JKeqmxY' title='Firefox (Mac) Privacy Walkthrough Video' target='_blank'>
                        <img src='/images/ff-logo.png' width='90' height='89' /><span class='label'>Firefox (Mac)</span>
                        <span class='volunteers-needed'>volunteers needed!</span>
                    </a>
                </li>
                <li class='enabled for-windows'>
                    <a href='http://www.youtube.com/watch?v=0_ICQbDwLs8' title='Firefox (Windows) Privacy Walkthrough Video' target='_blank'>
                        <img src='/images/ff-logo.png' width='90' height='89' /><span class='label'>Firefox (Windows)</span>
                        <span class='volunteers-needed'>volunteers needed!</span>
                    </a>
                </li>
            </ul>
        </p>

        <div class='clearfix'></div>

        <div class='go-to-discussions'>
            <em>
                If you still have trouble, you should
                <a href='http://www.facebook.com/pages/Reclaim-Privacy/121897834504447?v=app_2373072738'>
                    check out the discussion forums
                </a> on our Facebook Fan page, there are lots of
                other people there trying to help each other out.
            </em>
        </div>

    </div>

<!-- begin olark code -->
<script type="text/javascript">
(function(){document.write(unescape('%%3Cscript src=\\'' + (document.location.protocol == 'https:' ? "https:" : "http:") + '//static.olark.com/js/wc.js\\' type=\\'text/javascript\\'%%3E%%3C/script%%3E'));})();
</script><div id="olark-data"><a class="olark-key" id="olark-9122-608-10-8698" title="Powered by Olark" href="http://olark.com/about" rel="nofollow">Powered by Olark</a></div>
<script type="text/javascript">
(function(){
    var conf = wc_config();
    conf.vars.start_passive = 1;
    conf.vars.force_nickname = 'reclaimprivacy #' + Math.floor(Math.random()*1000);
    wc_init(null, conf);
})();
</script>
<!-- end olark code-->

</body>
</html>
            ''' % locals()

            # cache the page in memcache (only on the production servers)
            if 'reclaimprivacy.org' in parts.hostname:
                memcache.set(memcache_key, page_content)

        # write the response
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(page_content)


class Donations(webapp.RequestHandler):
    def get(self):

        # build the memcache key we will use
        version = VERSION
        memcache_key = 'page_content:donations:%(version)s' % locals()

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

            # render the page
            leftbar_content = _get_leftbar_content()
            page_content = '''
<html>
<head>
    <title>ReclaimPrivacy.org | Facebook Privacy Scanner</title>
    <link rel="stylesheet" href="/stylesheets/main.css" type="text/css" media="screen" title="no title" charset="utf-8">

</head>
<body>

    <div id='logo'>
        %(leftbar_content)s
    </div>

    <div id='content'>

        <h1>How will donations be used?</h1>
        <p>
            In the spirit of transparency, all donation amounts will be made public,
            and their allocation details will appear here.  These donations will be
            used to fund the operations of ReclaimPrivacy.org, <strong>not for profit</strong>.
        </p>
        <p>
            Current allocations for donations:
            <ul>
                <li>server costs (currently between $2 and $6 per day)</li>
                <li>advertising costs (strictly to spread privacy awareness)</li>
                <li>bounties to encourage creation of additional privacy scans</li>
            </ul>
            If you disagree with this policy, please email me at donations@reclaimprivacy.org
        </p>

        <h1>What has been raised so far?</h1>
        <p>
            As of Thursday, May 27th, the amount is about
            <span class='donation-amount'>$3006</span>, donated by <span class='donation-people'>313 people</span>.
        </p>
        <p>
            <em class='soft'>
                Right now, Pledgie is not listing donors because the Paypal account
                is delayed pending verification (donations don't clear until that happens, hopefully in 2 days).
            </em>
        </p>

        <h1>How can I donate?</h1>
        <p>
            You can donate via this Pledgie link (Paypal is one of the options):
            <br/>
            <br/>
            <a href='http://www.pledgie.com/campaigns/10721'><img alt='Click here to lend your support to: reclaimprivacy and make a donation at www.pledgie.com !' src='http://www.pledgie.com/campaigns/10721.png?skin_name=chrome' border='0' width='149' height='37' /></a>
        </p>

        <h1>Can I donate towards a nice dinner for you folks instead?</h1>
        <p>
            Yep.  We don't have a separate donation button for that, but if you leave
            a note on your donation marking it for personal use, we are happy to accept!
        </p>

    </div>

<!-- begin olark code -->
<script type="text/javascript">
(function(){document.write(unescape('%%3Cscript src=\\'' + (document.location.protocol == 'https:' ? "https:" : "http:") + '//static.olark.com/js/wc.js\\' type=\\'text/javascript\\'%%3E%%3C/script%%3E'));})();
</script><div id="olark-data"><a class="olark-key" id="olark-9122-608-10-8698" title="Powered by Olark" href="http://olark.com/about" rel="nofollow">Powered by Olark</a></div>
<script type="text/javascript">
(function(){
    var conf = wc_config();
    conf.vars.start_passive = 1;
    conf.vars.force_nickname = 'reclaimprivacy #' + Math.floor(Math.random()*1000);
    wc_init(null, conf);
})();
</script>
<!-- end olark code-->

</body>
</html>
            ''' % locals()

            # cache the page in memcache (only on the production servers)
            if 'reclaimprivacy.org' in parts.hostname:
                memcache.set(memcache_key, page_content)

        # write the response
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(page_content)


def _get_leftbar_content():
    return '''
        <a href="/"><img src='/images/logo.png?cb=2' width='200' height='200' /></a>
        <div class='donation-box'>
            <a href='http://www.pledgie.com/campaigns/10721'><img alt='Click here to lend your support to: reclaimprivacy and make a donation at www.pledgie.com !' src='http://www.pledgie.com/campaigns/10721.png?skin_name=chrome' border='0' width='149' height='37' /></a>
            <br/>
            <span class='donation-summary'>
                <strong class='amount'>$3006</strong> raised from <strong class='people'>313</strong> people
            </span>
            <br/>
            <a class='soft' href='/donations'>how will donations be used?</a>
        </div>
        <div class='press-links'>
            <a href='http://lifehacker.com/5540495/reclaimprivacy-bookmarklet-rates-your-facebook-exposure-levels' id='press-lifehacker' title='Lifehacker'><span>Lifehacker</span></a>
            <a href='http://www.wired.com/epicenter/2010/05/facebook-transparency-tool/' id='press-wired' title='Wired Magazine'><span>Wired Magazine</span></a>
            <a href='http://blogs.forbes.com/firewall/2010/05/17/facebook-scanner-helps-you-reclaim-your-privacy/' id='press-forbes' title='Forbes Firewall Blog'><span>Forbes Firewall Blog</span></a>
            <a href='http://social.venturebeat.com/2010/05/17/reclaim-privacy/' id='press-venturebeat' title='Venturebeat'><span>Venturebeat</span></a>
            <a href='http://www.pcworld.com/article/196464/test_your_facebook_privacy_settings_heres_how.html' id='press-pcworld' title='PCWorld Magazine'><span>PCWorld Magazine</span></a>
            <a href='http://blogs.wsj.com/digits/2010/05/19/facebook-privacy-concerns-prompt-new-sites/?mod=rss_WSJBlog' id='press-wsj' title='Wall Street Journal Blog'><span>Wall Street Journal Blog</span></a>
        </div>
'''

application = webapp.WSGIApplication([
    ('/newsletter', Newsletter),
    ('/desktop-app', DesktopApp),
    ('/facebook', Facebook),
    ('/help', Help),
    ('/donations', Donations),
    ('/', Facebook),
], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()


