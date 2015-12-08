from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# TODO: move app_id/machine ID from string to GUID?
def create_all(engine):
    Base.metadata.create_all(bind = engine)
    
class Server():
    """
        server props. HINT: does not stored to database 
    """    
    def __init__(self):
        self.title = 'WinCE open-source MDM Server'
        self.version = '2015.12'  
        self.name = '192.168.1.1'

class Device(Base):    
    """ 
        window ce / mobile device parameters
        HINT: devices that have no device_id not supported at all 
    """

    __tablename__ = 'device'
    
    """ received DeviceId (mandatory) """
    id = Column(String(64), primary_key=True)
    
    """
        These parameters received and ser from poll request 
    """
    
    """ @var management_system: string - management system name """ 
    management_system = Column(String(128))
    
    """ @var management_version: string - management system version """ 
    management_version = Column(String(50))
    
    """ @var name: string - device name """ 
    name = Column(String(128))

    """ @var username: string - user name, windows CE 4.2 reports it as domainname\username """
    username = Column(String(64))
    
    """ @var platform: string - device platform identification string """
    platform = Column(String(64))
    
    """ @var processor: string - device processor identification string """
    processor = Column(String(64))
    
    """ @var ip_address: string - device's default network adapter ipv4 address """
    ip_address = Column(String(16))
    
    """ @var ip_subnet: string - device's default network adapter ipv4 subnet """
    ip_subnet = Column(String(16))

    """ @var codepage: string - device codepage """
    codepage = Column(String(16))
    
    """ @var default_locale_id: string - device's system default locale id """
    default_locale_id = Column(String(16))

    """
        These parameters always will be sent to device on next device poll request
    """
        
    """ @var poll_interval: - poll interval """
    poll_interval = Column(Integer)
    
    """ @var failure_retry - failure retry count (if action fails) """
    failure_retry = Column(Integer)
    
    """ @var failure_interval - time between action retry """
    failure_interval = Column(Integer)


    """ @var software_report_enable - device will report about installed software """
    software_report_enable = Column(Boolean)
    
    """ @var software_report_interval - how often reports will be done """
    software_report_interval = Column(Integer)
    
    """ @var software_report_filter - filter for software??? """
    software_report_filter = Column(String(255))
    
    """ @var software_report_path - path for software??? """
    software_report_path = Column(String(255))
    
    """ @var software_report_recursive - use recursion to search """
    software_report_recursive = Column(Boolean)
    
    """ @var software_report_compressed - search compressed items """
    software_report_compressed = Column(Boolean)
    
    """ @var software_report_encrypted - search encrypted items """
    software_report_encrypted = Column(Boolean)
    

    """ @var file_report_enable - device will report specified files contents """
    file_report_enable = Column(Boolean)
    
    """ @var file_report_interval - how often reports will be done """
    file_report_interval = Column(Integer)
    
    """ @var file_report_filter - filter for files??? """
    file_report_filter = Column(String(255))
    
    """ @var file_report_path - path for files??? """
    file_report_path = Column(String(255))
    
    """ @var file_report_recursive - use recursion to search """
    file_report_recursive = Column(Boolean)
    
    """ @var file_report_compressed - search compressed items """
    file_report_compressed = Column(Boolean)
    
    """ @var file_report_encrypted - search encrypted items """
    file_report_encrypted = Column(Boolean)

    
    """ @var hardware_report_enable - enable hardware report (inventory list) """
    hardware_report_enable = Column(Boolean)
    
    """ @var hardware_report_interval - how often reports will be done """
    hardware_report_interval = Column(Integer)

    def __init__(self):
        self.name = 'Unknown device'
        self.poll_interval = 60 
        self.failure_retry = 10
        self.failure_interval = 600
        self.software_report_enable = False
        self.software_report_interval = 60
        self.software_report_compressed = True
        self.software_report_encrypted = True
        self.software_report_recursive = True
        self.software_report_path = ""
        self.software_report_filter = ""
        self.file_report_enable = False
        self.file_report_interval = 60
        self.filee_report_compressed = True
        self.file_report_encrypted = True
        self.file_report_recursive = True
        self.file_report_filter = ""
        self.file_report_path = ""
        self.hardware_report_enable = False
        self.hardware_report_interval = 60
        
class Package(Base):
    """
       represent information about package
    """
    
    __tablename__ = 'package'
    
    id = Column(String(64), primary_key = True)


class AssignedPackage(Base):
    """
        represent package need to be installed on device
    """
    __tablename__ = 'assigned_package'

    id = Column(Integer, primary_key = True)
    package = Column(String(64), ForeignKey('package.id'))
    device = Column(String(64), ForeignKey('device.id'))
    