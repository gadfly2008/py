#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from controller import get_blocks

def block_monitor(logger, hostname):
    blocks = [b.strip() for b in get_blocks(logger)]
    args = []
    names = []
    mail_body = {}
    for b in blocks:
        try:
            if b:
                used, name = b.split(" ")
                names.append(name)
                used = int(used.split("%")[0])
                if used > 80:
                    mail_body[name] = used
                    args.append({"hostname": hostname, "used": used, "name": name, "level": "3"})
                else:
                    args.append({"hostname": hostname, "used": used, "name": name, "level": "0"})
        except Exception, e:
            logger.error("Error %s in %s" %(e, b))

    logger.debug("Get blocks complete.")
    return {"mail": mail_body, "block": args, "names": names}