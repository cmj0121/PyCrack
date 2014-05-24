SUBDIR=


.PHONY: all $(SUBDIR) test

all: $(SUBDIR) deploy

$(SUBDIR):
	$(MAKE) -C $@ $(MAKECMDGOALS)

test: $(SUBDIR)
	

.PHONY: clean

clean: $(SUBDIR)
	sudo rm -rf build/ dist/ *egg-info/ modules 
	find . | grep .pyc$ | xargs rm 2>/dev/null || true

.PHONY: deploy

deploy:
	./setup.py build
	sudo ./setup.py install
