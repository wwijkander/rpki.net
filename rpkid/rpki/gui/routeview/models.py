import django.db.models
import rpki.gui.models

class RouteOrigin(rpki.gui.models.PrefixV4):
    "Represents an IPv4 BGP routing table entry."

    asn = django.db.models.PositiveIntegerField(help_text='origin AS', null=False)
        
    def __unicode__(self):
        return u"AS%d's route origin for %s" % (self.asn, self.get_prefix_display())

class RouteOriginV6(rpki.gui.models.PrefixV6):
    "Represents an IPv6 BGP routing table entry."

    asn = django.db.models.PositiveIntegerField(help_text='origin AS', null=False)
        
    def __unicode__(self):
        return u"AS%d's route origin for %s" % (self.asn, self.get_prefix_display())

# vim:sw=4 ts=8 expandtab
