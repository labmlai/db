import fcntl
import time

from labml import logger


def main():
    logger.log('open')
    with open('test.lock', 'w') as f:
        logger.log('lock')
        fcntl.lockf(f, fcntl.LOCK_EX)
        logger.log('locked')
        f.write('test')
        time.sleep(10)

    logger.log('done')


if __name__ == '__main__':
    main()
