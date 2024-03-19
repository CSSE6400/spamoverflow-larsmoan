from spamoverflow.models.spamoverflow import Domain, DomainCount, Email
from sqlalchemy import func
from spamoverflow.models import db
from datetime import datetime


#This function will periodically be run every two minutes and will update a current list of the domains found in all scan requests present in the database
def update_domains_count():
    #query_result = Domain.query.with_entities(Domain.link, func.count(Domain.link)).group_by(Domain.link).all()
    query_result = (
        db.session.query(Domain.link, Email.customer_id, func.count(Domain.link))
        .join(Email)
        .group_by(Domain.link, Email.customer_id)
        .all()
    )
    for domain, customer_id, count in query_result:
        entry = DomainCount.query.filter_by(id=domain, customer_id=customer_id).first()

        if entry:
            entry.count = count
            entry.updated_at = datetime.utcnow()
        else:
            entry = DomainCount(id = domain, customer_id = customer_id, count = count)
            db.session.add(entry)
        db.session.commit()

