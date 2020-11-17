import fcntl
import time

from labml import logger


def main():
    logger.log('open')
    with open('test.lock', 'r') as f:
        logger.log('lock')
        fcntl.lockf(f, fcntl.LOCK_SH)
        logger.log('locked')
        time.sleep(10)

    logger.log('done')


if __name__ == '__main__':
    main()
