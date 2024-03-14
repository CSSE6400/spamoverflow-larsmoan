from spamoverflow.models.spamoverflow import Domain, DomainCount
from sqlalchemy import func
from spamoverflow.models import db


#This function will periodically be run every two minutes and will update a current list of the domains found in all scan requests present in the database
def update_domains_count():
    query_result = Domain.query.with_entities(Domain.link, func.count(Domain.link)).group_by(Domain.link).all()
    for domain, count in query_result:
        entry = DomainCount.query.get(domain)
        if entry:
            entry.count = count
            db.session.commit()
        else:
            entry = DomainCount(id = domain, count = count)
            db.session.add(entry)
            db.session.commit()

#TODO Create a periodic task that checks if there are any pending scan requests sorted by priority or not and scans them. Alters the appropriate malicious flag etc
