import os, sys

try:
    import machine
except:
    pass

try:
    import utime as time
except:
    import time

try:
    import configurations
except:
    pass

try:
    import adl as adl
except:
    # fooling the IDE
    pass


class Amot:
    @staticmethod
    def configApp(conf):
        return AmotEngine.getInstance().config(conf, mode='App')

    @staticmethod
    def configEnv(conf):
        return AmotEngine.getInstance().config(conf, mode='Env')

    @staticmethod
    def proxy():
        return AmotEngine.getInstance().starter()

    @staticmethod
    def attached(component):
        return AmotEngine.getInstance().attached(component)

    @staticmethod
    def env(data):
        return AmotEngine.getInstance().conf.get(data)

    @staticmethod
    def agent():
        return AmotEngine.getInstance().agent

    @staticmethod
    def instance():
        return AmotEngine.getInstance()


class AmotEngine:
    _instance = None

    @staticmethod
    def setInstanceWith(ip, agent, conf):
        if AmotEngine._instance == None:
            AmotEngine._instance = AmotEngine(ip, agent, conf)

    @staticmethod
    def getInstance():
        return AmotEngine._instance

    def config(self, conf, mode):
        if mode == 'App':
            return configurations.configurations['application'][conf]
        elif mode == 'Env':
            return configurations.configurations['environment'][conf]
        else:
            return configurations.configurations['device'][conf]

    def starter(self):
        return self.current_components[self.configuration['start']]

    def attached(self, component):
        class_name = component.__class__.__name__
        next_class = self.attachments.get(class_name)
        next_object = self.current_components[next_class]
        return next_object


    def __init__(self, ip, agent, conf):
        self.ip = ip
        self.conf = conf
        self.app = None
        self.agent = agent
        self.last_adaptation = 0

        self.current_components = self.loadComponents()
        self.attachments = adl.adl['attachments']
        self.configuration = adl.adl['configuration']
        self.adaptability = adl.adl['adaptability']

    def loadComponents(self):
        import configurations
        current_components = {}
        components = adl.adl['components']
        for component in components:
            component_file = components.get(component)

            # ATENÇÃO AQUI: O import é forçado dentro do pacote 'components'
            namespace = __import__('components.' + component_file)

            component_module = getattr(namespace, component_file)
            setattr(component_module, 'configurations', configurations)
            component_instance = getattr(component_module, component)
            current_components[component] = component_instance()
        return current_components

    def run(self, app):
        self.app = app

        if self.last_adaptation == 0:
            self.last_adaptation = time.time()

        self.app.setup()

        while True:
            try:
                # Loop principal da aplicação
                self.app.loop()

                # Verifica se precisa adaptar (recarregar componentes)
                self.checkAdaptation()

            except OSError as e:
                print(e)
                AmotEngine.restartAndReconnect()

    def checkAdaptation(self):
        if (self.adaptability['type'] not in ['', None]
                and (time.time() - self.last_adaptation) > self.adaptability['timeout']):
            isthere_adaptation = self.agent.adapt()
            if isthere_adaptation:
                self.reload_components()
            self.last_adaptation = time.time()

    def reload_components(self):
        # Lógica para recarregar módulos sem reiniciar o Python
        del sys.modules['adl']
        del sys.modules['configurations']

        new_adl = __import__('adl')
        new_configurations = __import__('configurations')

        sys.modules['adl'] = new_adl
        sys.modules['configurations'] = new_configurations

        self.components = new_adl.adl['components']
        self.attachments = new_adl.adl['attachments']
        self.adaptability = new_adl.adl['adaptability']

        # Limpa módulos antigos de components
        for module in [module for module in sys.modules.keys() if module[:11] == 'components.']:
            del sys.modules[module]

        # Recarrega componentes
        for component in self.components:
            component_file = self.components.get(component)
            namespace = __import__('components.' + component_file)
            component_module = getattr(namespace, component_file)
            component_instance = getattr(component_module, component)
            self.current_components[component] = component_instance()

        import configurations
        app_module = __import__('app')
        setattr(app_module, 'configurations', new_configurations)
        app_instance = getattr(app_module, 'App')
        self.app = app_instance()