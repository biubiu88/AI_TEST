"""
数据工厂服务
提供各种数据生成和处理工具
"""
import json
import random
import string
import hashlib
import base64
import re
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Union
import pytz
from dateutil.parser import parse as date_parse


class DataFactoryService:
    """
    数据工厂服务类
    提供各种数据生成和处理工具
    """

    # 中文姓名常用姓氏和名字
    CHINESE_LAST_NAMES = [
        '王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴', '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗',
        '梁', '宋', '郑', '谢', '韩', '唐', '冯', '于', '董', '萧', '程', '曹', '袁', '邓', '许', '傅', '沉', '曾', '彭', '吕',
        '苏', '卢', '蒋', '蔡', '贾', '丁', '魏', '薛', '叶', '阎', '余', '潘', '杜', '戴', '夏', '钟', '汪', '田', '任', '姜',
        '范', '方', '石', '姚', '谭', '廖', '邹', '熊', '金', '陆', '郝', '孔', '白', '崔', '康', '毛', '邱', '秦', '江', '史',
        '顾', '侯', '邵', '孟', '龙', '万', '段', '雷', '钱', '汤', '尹', '黎', '易', '常', '武', '乔', '贺', '赖', '龚', '文'
    ]

    CHINESE_FIRST_NAMES_MALE = [
        '伟', '强', '磊', '军', '洋', '勇', '涛', '超', '辉', '刚', '平', '辉', '鹏', '峰', '明', '华', '飞', '鑫', '波', '斌',
        '宇', '浩', '俊', '杰', '涛', '磊', '峰', '超', '辉', '凯', '亮', '阳', '林', '东', '伟', '宁', '建', '辉', '强', '龙',
        '博', '轩', '帅', '晨', '曦', '宇', '航', '瑞', '杰', '豪', '然', '成', '诚', '诚', '城', '程', '承', '丞', '创', '楚'
    ]

    CHINESE_FIRST_NAMES_FEMALE = [
        '敏', '静', '丽', '霞', '芳', '娜', '秀英', '丹', '红', '艳', '娜', '敏', '丽', '静', '霞', '萍', '莉', '娟', '春', '梅',
        '燕', '蓉', '琴', '瑛', '芬', '洁', '怡', '琳', '璐', '婷', '雪', '慧', '颖', '瑶', '娜', '慧', '倩', '舒', '婉', '雅',
        '诗', '韵', '柔', '馨', '蕊', '蕾', '蕾', '蕾', '蕾', '蕾', '蕾', '蕾', '蕾', '蕾', '蕾', '蕾', '蕾', '蕾', '蕾', '蕾'
    ]

    CHINESE_CITIES = [
        '北京', '上海', '广州', '深圳', '杭州', '南京', '武汉', '成都', '西安', '重庆', '天津', '苏州', '长沙', '青岛', '大连',
        '厦门', '宁波', '无锡', '合肥', '福州', '济南', '石家庄', '郑州', '太原', '沈阳', '长春', '哈尔滨', '昆明', '贵阳', '南宁',
        '兰州', '西宁', '银川', '乌鲁木齐', '拉萨', '呼和浩特', '南昌', '海口', '三亚', '桂林', '温州', '东莞', '佛山', '中山', '珠海'
    ]

    CHINESE_DISTRICTS = [
        '朝阳区', '海淀区', '浦东新区', '天河区', '越秀区', '福田区', '罗湖区', '南山区', '宝安区', '西湖区', '上城区', '下城区',
        '鼓楼区', '玄武区', '江岸区', '武昌区', '锦江区', '青羊区', '高新区', '锦江区', '雁塔区', '碑林区', '渝中区', '江北区',
        '和平区', '河东区', '河西区', '南开区', '吴江区', '姑苏区', '天心区', '岳麓区', '芙蓉区', '市南区', '市北区', '黄岛区'
    ]

    CHINESE_STREETS = [
        '建设路', '人民路', '解放路', '胜利路', '文化路', '科技路', '花园路', '朝阳路', '友谊路', '健康路', '幸福路', '平安路',
        '和谐路', '振兴路', '工业路', '商业路', '学府路', '大学路', '青年路', '中山路', '长江路', '黄河路', '长城路', '天山路'
    ]

    EMAIL_DOMAINS = [
        'qq.com', '163.com', '126.com', 'gmail.com', 'hotmail.com', 'yahoo.com', 'sina.com', 'sohu.com', 'foxmail.com'
    ]

    COMPANY_TYPES = [
        '有限公司', '股份有限公司', '有限责任公司', '集团有限公司', '科技有限公司', '贸易有限公司', '投资有限公司', '发展有限公司',
        '实业有限公司', '咨询有限公司', '网络有限公司', '电子商务有限公司', '信息技术有限公司', '文化传媒有限公司'
    ]

    def __init__(self):
        pass

    # ==================== 测试数据工具 ====================
    
    @staticmethod
    def generate_chinese_name(gender: str = 'random', count: int = 1) -> Union[str, List[str]]:
        """
        生成中文姓名
        :param gender: 性别 ('male', 'female', 'random')
        :param count: 生成数量
        :return: 生成的姓名或姓名列表
        """
        names = []
        for _ in range(count):
            last_name = random.choice(DataFactoryService.CHINESE_LAST_NAMES)
            
            if gender == 'male':
                first_name = random.choice(DataFactoryService.CHINESE_FIRST_NAMES_MALE)
            elif gender == 'female':
                first_name = random.choice(DataFactoryService.CHINESE_FIRST_NAMES_FEMALE)
            else:  # random
                all_first_names = DataFactoryService.CHINESE_FIRST_NAMES_MALE + DataFactoryService.CHINESE_FIRST_NAMES_FEMALE
                first_name = random.choice(all_first_names)
            
            name = last_name + first_name
            names.append(name)
        
        return names[0] if count == 1 else names

    @staticmethod
    def generate_chinese_phone(region: str = 'all', count: int = 1) -> Union[str, List[str]]:
        """
        生成中文手机号
        :param region: 地区 ('all', 'mobile', 'unicom', 'telecom')
        :param count: 生成数量
        :return: 生成的手机号或手机号列表
        """
        phones = []
        
        # 三大运营商号段
        MOBILE_PREFIXES = ['134', '135', '136', '137', '138', '139', '147', '150', '151', '152', '157', '158', '159', '178', '182', '183', '184', '187', '188', '198']
        UNICOM_PREFIXES = ['130', '131', '132', '145', '155', '156', '166', '175', '176', '185', '186', '196']
        TELECOM_PREFIXES = ['133', '149', '153', '173', '177', '180', '181', '189', '191', '199']
        
        all_prefixes = MOBILE_PREFIXES + UNICOM_PREFIXES + TELECOM_PREFIXES
        
        if region == 'mobile':
            prefixes = MOBILE_PREFIXES
        elif region == 'unicom':
            prefixes = UNICOM_PREFIXES
        elif region == 'telecom':
            prefixes = TELECOM_PREFIXES
        else:  # all
            prefixes = all_prefixes
        
        for _ in range(count):
            prefix = random.choice(prefixes)
            suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
            phone = prefix + suffix
            phones.append(phone)
        
        return phones[0] if count == 1 else phones

    @staticmethod
    def generate_chinese_email(domain: str = 'random', count: int = 1) -> Union[str, List[str]]:
        """
        生成中文邮箱
        :param domain: 邮箱域名 ('random', 'qq.com', '163.com', etc.)
        :param count: 生成数量
        :return: 生成的邮箱或邮箱列表
        """
        emails = []
        
        for _ in range(count):
            # 生成用户名：中文姓名拼音或随机字母数字组合
            if random.choice([True, False]):
                # 使用中文姓名作为用户名
                name = DataFactoryService.generate_chinese_name()
                username = name.lower().replace(' ', '')
            else:
                # 随机字母数字组合
                username_length = random.randint(6, 12)
                username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=username_length))
            
            # 选择域名
            if domain == 'random':
                selected_domain = random.choice(DataFactoryService.EMAIL_DOMAINS)
            else:
                selected_domain = domain
            
            email = f"{username}@{selected_domain}"
            emails.append(email)
        
        return emails[0] if count == 1 else emails

    @staticmethod
    def generate_chinese_address(full_address: bool = True, count: int = 1) -> Union[str, List[str]]:
        """
        生成中文地址
        :param full_address: 是否生成完整地址
        :param count: 生成数量
        :return: 生成的地址或地址列表
        """
        addresses = []
        
        for _ in range(count):
            city = random.choice(DataFactoryService.CHINESE_CITIES)
            district = random.choice(DataFactoryService.CHINESE_DISTRICTS)
            street = random.choice(DataFactoryService.CHINESE_STREETS)
            house_number = f"{random.randint(1, 999)}号"
            
            if full_address:
                address = f"{city}{district}{street}{house_number}"
            else:
                address = f"{district}{street}{house_number}"
            
            addresses.append(address)
        
        return addresses[0] if count == 1 else addresses

    @staticmethod
    def generate_company_name(company_type: str = 'all', count: int = 1) -> Union[str, List[str]]:
        """
        生成公司名称
        :param company_type: 公司类型 ('all' 或具体类型)
        :param count: 生成数量
        :return: 生成的公司名称或公司名称列表
        """
        company_names = []
        
        for _ in range(count):
            # 生成公司名称前缀
            prefix_parts = random.randint(2, 4)
            company_prefix = ''.join([random.choice(string.ascii_uppercase) for _ in range(prefix_parts)]) + '科技'
            
            # 选择公司类型
            if company_type == 'all':
                selected_type = random.choice(DataFactoryService.COMPANY_TYPES)
            else:
                selected_type = company_type
            
            company_name = f"{company_prefix}{selected_type}"
            company_names.append(company_name)
        
        return company_names[0] if count == 1 else company_names

    # ==================== 字符工具 ====================

    @staticmethod
    def remove_whitespace(text: str) -> Dict[str, Any]:
        """
        去除空格换行
        :param text: 输入文本
        :return: 处理结果
        """
        result = {
            'original_text': text,
            'cleaned_text': re.sub(r'\s+', '', text),
            'removed_chars': len(re.findall(r'\s', text))
        }
        return result

    @staticmethod
    def replace_string(text: str, old_str: str, new_str: str, is_regex: bool = False) -> Dict[str, Any]:
        """
        字符串替换
        :param text: 输入文本
        :param old_str: 被替换的字符串
        :param new_str: 替换的字符串
        :param is_regex: 是否使用正则表达式
        :return: 处理结果
        """
        if is_regex:
            result = re.sub(old_str, new_str, text)
            count = len(re.findall(old_str, text))
        else:
            result = text.replace(old_str, new_str)
            count = text.count(old_str)
        
        return {
            'original_text': text,
            'replaced_text': result,
            'replaced_count': count
        }

    @staticmethod
    def escape_string(text: str, escape_type: str = 'json') -> Dict[str, Any]:
        """
        字符串转义
        :param text: 输入文本
        :param escape_type: 转义类型 ('json', 'html', 'url', 'xml')
        :return: 处理结果
        """
        if escape_type == 'json':
            escaped_text = json.dumps(text)[1:-1]  # 移除外层引号
        elif escape_type == 'html':
            escaped_text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#x27;')
        elif escape_type == 'url':
            escaped_text = re.sub(r'[^a-zA-Z0-9._~:/?#[\]@!$&\'()*+,;=-]', lambda x: '%' + x.group(0).encode('utf-8').hex().upper(), text)
        elif escape_type == 'xml':
            escaped_text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
        else:
            escaped_text = text  # 默认不转义
        
        return {
            'original_text': text,
            'escaped_text': escaped_text,
            'escape_type': escape_type
        }

    @staticmethod
    def unescape_string(text: str, unescape_type: str = 'json') -> Dict[str, Any]:
        """
        字符串反转义
        :param text: 输入文本
        :param unescape_type: 反转义类型 ('json', 'html', 'url', 'xml')
        :return: 处理结果
        """
        if unescape_type == 'json':
            unescaped_text = json.loads(f'"{text}"')
        elif unescape_type == 'html':
            unescaped_text = text.replace('&quot;', '"').replace('&#x27;', "'").replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')
        elif unescape_type == 'url':
            import urllib.parse
            unescaped_text = urllib.parse.unquote(text)
        elif unescape_type == 'xml':
            unescaped_text = text.replace('&quot;', '"').replace('&apos;', "'").replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')
        else:
            unescaped_text = text  # 默认不反转义
        
        return {
            'original_text': text,
            'unescaped_text': unescaped_text,
            'unescape_type': unescape_type
        }

    @staticmethod
    def word_count(text: str) -> Dict[str, Any]:
        """
        字数统计
        :param text: 输入文本
        :return: 统计结果
        """
        import re
        
        # 字符总数（包括空格）
        char_total = len(text)
        
        # 字符总数（不包括空格）
        char_no_spaces = len(text.replace(' ', ''))
        
        # 单词数（按空格分割）
        words = len(text.split())
        
        # 中文字符数
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        
        # 英文字母数
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        # 数字字符数
        digits = len(re.findall(r'\d', text))
        
        # 行数
        lines = len(text.split('\n'))
        
        return {
            'char_total': char_total,
            'char_no_spaces': char_no_spaces,
            'words': words,
            'chinese_chars': chinese_chars,
            'english_chars': english_chars,
            'digits': digits,
            'lines': lines
        }

    @staticmethod
    def text_diff(text1: str, text2: str) -> Dict[str, Any]:
        """
        文本对比
        :param text1: 第一个文本
        :param text2: 第二个文本
        :return: 对比结果
        """
        import difflib
        
        # 计算相似度
        similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
        
        # 生成详细差异
        differ = difflib.Differ()
        diff_lines = list(differ.compare(text1.splitlines(), text2.splitlines()))
        
        # 统计差异
        added_lines = len([line for line in diff_lines if line.startswith('+ ')])
        removed_lines = len([line for line in diff_lines if line.startswith('- ')])
        changed_lines = len([line for line in diff_lines if line.startswith('? ')])
        
        return {
            'similarity': round(similarity, 4),
            'added_lines': added_lines,
            'removed_lines': removed_lines,
            'changed_lines': changed_lines,
            'total_lines': max(len(text1.splitlines()), len(text2.splitlines())),
            'diff_details': diff_lines
        }

    @staticmethod
    def regex_test(pattern: str, text: str, flags: str = '') -> Dict[str, Any]:
        """
        正则测试
        :param pattern: 正则表达式模式
        :param text: 要测试的文本
        :param flags: 标志（如 'i' 忽略大小写, 'm' 多行匹配等）
        :return: 测试结果
        """
        import re
        
        # 构建标志
        re_flags = 0
        if 'i' in flags:
            re_flags |= re.IGNORECASE
        if 'm' in flags:
            re_flags |= re.MULTILINE
        if 's' in flags:
            re_flags |= re.DOTALL
        
        try:
            matches = re.findall(pattern, text, flags=re_flags)
            match_count = len(matches)
            
            # 获取详细匹配信息
            detailed_matches = []
            for match in re.finditer(pattern, text, flags=re_flags):
                detailed_matches.append({
                    'match': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'groups': match.groups()
                })
            
            return {
                'pattern': pattern,
                'text': text,
                'matches': matches,
                'match_count': match_count,
                'detailed_matches': detailed_matches,
                'flags': flags,
                'success': True
            }
        except re.error as e:
            return {
                'pattern': pattern,
                'text': text,
                'error': str(e),
                'success': False
            }

    @staticmethod
    def case_convert(text: str, convert_type: str = 'upper') -> Dict[str, Any]:
        """
        大小写转换
        :param text: 输入文本
        :param convert_type: 转换类型 ('upper', 'lower', 'capitalize', 'title', 'swapcase')
        :return: 转换结果
        """
        if convert_type == 'upper':
            converted_text = text.upper()
        elif convert_type == 'lower':
            converted_text = text.lower()
        elif convert_type == 'capitalize':
            converted_text = text.capitalize()
        elif convert_type == 'title':
            converted_text = text.title()
        elif convert_type == 'swapcase':
            converted_text = text.swapcase()
        else:
            converted_text = text  # 默认不转换
        
        return {
            'original_text': text,
            'converted_text': converted_text,
            'convert_type': convert_type
        }

    @staticmethod
    def string_format(text: str, format_type: str = 'trim') -> Dict[str, Any]:
        """
        字符串格式化
        :param text: 输入文本
        :param format_type: 格式化类型 ('trim', 'reverse', 'split', 'join')
        :return: 格式化结果
        """
        if format_type == 'trim':
            formatted_text = text.strip()
        elif format_type == 'reverse':
            formatted_text = text[::-1]
        elif format_type == 'split':
            # 按空格分割
            formatted_text = text.split()
        elif format_type == 'join':
            # 如果输入是列表，则连接；否则按字符连接
            if isinstance(text, list):
                formatted_text = ' '.join(text)
            else:
                formatted_text = ' '.join(list(text))
        else:
            formatted_text = text  # 默认不格式化
        
        return {
            'original_text': text,
            'formatted_text': formatted_text,
            'format_type': format_type
        }

    # ==================== 随机工具 ====================

    @staticmethod
    def random_int(min_val: int = 1, max_val: int = 100, count: int = 1) -> Union[int, List[int]]:
        """
        生成随机整数
        :param min_val: 最小值
        :param max_val: 最大值
        :param count: 生成数量
        :return: 生成的随机整数或整数列表
        """
        if count == 1:
            return random.randint(min_val, max_val)
        else:
            return [random.randint(min_val, max_val) for _ in range(count)]

    @staticmethod
    def random_float(min_val: float = 0.0, max_val: float = 1.0, precision: int = 2, count: int = 1) -> Union[float, List[float]]:
        """
        生成随机浮点数
        :param min_val: 最小值
        :param max_val: 最大值
        :param precision: 精度（小数位数）
        :param count: 生成数量
        :return: 生成的随机浮点数或浮点数列表
        """
        if count == 1:
            return round(random.uniform(min_val, max_val), precision)
        else:
            return [round(random.uniform(min_val, max_val), precision) for _ in range(count)]

    @staticmethod
    def random_string(length: int = 8, char_type: str = 'all', count: int = 1) -> Union[str, List[str]]:
        """
        生成随机字符串
        :param length: 字符串长度
        :param char_type: 字符类型 ('all', 'letters', 'lowercase', 'uppercase', 'digits', 'alphanumeric', 'hex', 'chinese', 'special')
        :param count: 生成数量
        :return: 生成的随机字符串或字符串列表
        """
        if char_type == 'letters':
            chars = string.ascii_letters
        elif char_type == 'lowercase':
            chars = string.ascii_lowercase
        elif char_type == 'uppercase':
            chars = string.ascii_uppercase
        elif char_type == 'digits':
            chars = string.digits
        elif char_type == 'alphanumeric':
            chars = string.ascii_letters + string.digits
        elif char_type == 'hex':
            chars = string.digits + 'abcdef'
        elif char_type == 'chinese':
            # 生成中文字符（这里简单使用常用汉字）
            chinese_chars = '的一是在不了有和人这中大为上个国我以要他时来用们生到作地于出就分对成会可主发年动同工也能下过子说产种面而方后多定行学法所民得经十三之进着等部度家电力里如水化高自二理起小物现实加量都两体制机当使点从业本去把性好应开它合还因由其些然前外天政四日那社义事平形相全表间样与关各重新线内数正心反你明看原又么利比或但质气第向道命此变条只没结解问意建月公无系军很情者最立代想已通并提直题党程展五果料象员革位入常文总次品式活设及管特件长求老头基资边流路级少图山统接知较将组见计别她手角期根论运农指几九区强放决西被干做必战先回则任取据处队南给色光门即保治北造百规热领七海口东导器压志世金增争济阶油思术极交受联什认六共权收证改清己美再采转更单风切打白教速花带安场身车例真务具万每目至达走积示议声报斗完类八离华名确才科张信马节话米整空元况今集温传土许步群广石记需段研界拉林律叫且究观越织装影算低持音众书布复容儿须际商非验连断深难近矿千周委素技备半办青省列习响约支般史感劳便团往酸历市克何除消构府称太准精值号率族维划选标写存候毛亲快效斯院查江型眼王按格养易置派层片始却专状育厂京识适属圆包火住调满县局照参红细引听该铁价严'
            chars = chinese_chars
        elif char_type == 'special':
            chars = string.punctuation
        else:  # all
            chars = string.ascii_letters + string.digits + string.punctuation
        
        results = []
        for _ in range(count):
            if char_type == 'chinese':
                result = ''.join(random.choices(chars, k=length))
            else:
                result = ''.join(random.choices(chars, k=length))
            results.append(result)
        
        return results[0] if count == 1 else results

    @staticmethod
    def random_uuid(version: int = 4, count: int = 1) -> Union[str, List[str]]:
        """
        生成随机UUID
        :param version: UUID版本 (1, 4)
        :param count: 生成数量
        :return: 生成的UUID或UUID列表
        """
        results = []
        for _ in range(count):
            if version == 1:
                result = str(uuid.uuid1())
            elif version == 4:
                result = str(uuid.uuid4())
            else:
                result = str(uuid.uuid4())  # 默认使用v4
            results.append(result)
        
        return results[0] if count == 1 else results

    @staticmethod
    def random_mac_address(separator: str = ':', count: int = 1) -> Union[str, List[str]]:
        """
        生成随机MAC地址
        :param separator: 分隔符 (':', '-', '')
        :param count: 生成数量
        :return: 生成的MAC地址或MAC地址列表
        """
        results = []
        for _ in range(count):
            mac = ':'.join(['{:02x}'.format(random.randint(0, 255)) for _ in range(6)])
            if separator != ':':
                mac = mac.replace(':', separator)
            results.append(mac.upper())
        
        return results[0] if count == 1 else results

    @staticmethod
    def random_ip_address(ip_version: int = 4, count: int = 1) -> Union[str, List[str]]:
        """
        生成随机IP地址
        :param ip_version: IP版本 (4, 6)
        :param count: 生成数量
        :return: 生成的IP地址或IP地址列表
        """
        results = []
        for _ in range(count):
            if ip_version == 4:
                ip = '.'.join(str(random.randint(1, 255)) for _ in range(4))
            elif ip_version == 6:
                # 简单生成IPv6格式（实际IPv6生成更复杂）
                ip = ':'.join('{:x}'.format(random.randint(0, 65535)) for _ in range(8))
            else:
                ip = '.'.join(str(random.randint(1, 255)) for _ in range(4))  # 默认IPv4
            results.append(ip)
        
        return results[0] if count == 1 else results

    @staticmethod
    def random_date(start_date: str = '2024-01-01', end_date: str = '2024-12-31', date_format: str = '%Y-%m-%d', count: int = 1) -> Union[str, List[str]]:
        """
        生成随机日期
        :param start_date: 开始日期
        :param end_date: 结束日期
        :param date_format: 日期格式
        :param count: 生成数量
        :return: 生成的日期或日期列表
        """
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        results = []
        for _ in range(count):
            delta = end_dt - start_dt
            random_days = random.randint(0, delta.days)
            random_date = start_dt + timedelta(days=random_days)
            results.append(random_date.strftime(date_format))
        
        return results[0] if count == 1 else results

    @staticmethod
    def random_boolean(count: int = 1) -> Union[bool, List[bool]]:
        """
        生成随机布尔值
        :param count: 生成数量
        :return: 生成的布尔值或布尔值列表
        """
        if count == 1:
            return random.choice([True, False])
        else:
            return [random.choice([True, False]) for _ in range(count)]

    @staticmethod
    def random_color(format: str = 'hex', count: int = 1) -> Union[str, List[str]]:
        """
        生成随机颜色
        :param format: 颜色格式 ('hex', 'rgb', 'rgba')
        :param count: 生成数量
        :return: 生成的颜色或颜色列表
        """
        results = []
        for _ in range(count):
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            a = random.randint(0, 100) / 100  # 透明度 0-1
            
            if format == 'hex':
                result = f"#{r:02x}{g:02x}{b:02x}"
            elif format == 'rgb':
                result = f"rgb({r}, {g}, {b})"
            elif format == 'rgba':
                result = f"rgba({r}, {g}, {b}, {a:.2f})"
            else:
                result = f"#{r:02x}{g:02x}{b:02x}"  # 默认hex格式
            
            results.append(result)
        
        return results[0] if count == 1 else results

    @staticmethod
    def random_password(length: int = 12, include_uppercase: bool = True, include_lowercase: bool = True, 
                       include_digits: bool = True, include_special: bool = True, count: int = 1) -> Union[str, List[str]]:
        """
        生成随机密码
        :param length: 密码长度
        :param include_uppercase: 包含大写字母
        :param include_lowercase: 包含小写字母
        :param include_digits: 包含数字
        :param include_special: 包含特殊字符
        :param count: 生成数量
        :return: 生成的密码或密码列表
        """
        results = []
        for _ in range(count):
            chars = ''
            if include_uppercase:
                chars += string.ascii_uppercase
            if include_lowercase:
                chars += string.ascii_lowercase
            if include_digits:
                chars += string.digits
            if include_special:
                chars += string.punctuation
            
            if not chars:
                chars = string.ascii_letters + string.digits  # 默认字符集
            
            password = ''.join(random.choice(chars) for _ in range(length))
            results.append(password)
        
        return results[0] if count == 1 else results

    @staticmethod
    def random_sequence(sequence: List[Any], count: int = 1, unique: bool = False) -> Union[Any, List[Any]]:
        """
        从序列中随机选择元素
        :param sequence: 输入序列
        :param count: 生成数量
        :param unique: 是否唯一
        :return: 生成的元素或元素列表
        """
        if not sequence:
            return None if count == 1 else []
        
        if unique and count > len(set(sequence)):
            # 如果要求唯一且数量超过序列长度，调整数量
            count = len(set(sequence))
        
        if unique:
            results = random.sample(sequence, count)
        else:
            results = [random.choice(sequence) for _ in range(count)]
        
        return results[0] if count == 1 else results

    # ==================== 编码工具 ====================

    @staticmethod
    def timestamp_convert(timestamp: str, convert_type: str = 'to_datetime', timestamp_unit: str = 'auto') -> Dict[str, Any]:
        """
        时间戳转换
        :param timestamp: 时间戳或日期时间字符串
        :param convert_type: 转换类型 ('to_datetime', 'to_timestamp', 'current_timestamp')
        :param timestamp_unit: 时间戳单位 ('auto', 'second', 'millisecond')
        :return: 转换结果
        """
        try:
            if convert_type == 'current_timestamp':
                # 返回当前时间戳
                now = datetime.now()
                return {
                    'timestamp': int(now.timestamp()),
                    'timestamp_ms': int(now.timestamp() * 1000),
                    'datetime': now.isoformat(),
                    'timezone': str(now.astimezone().tzinfo)
                }
            elif convert_type == 'to_datetime':
                # 时间戳转日期时间
                ts = float(timestamp)
                
                # 判断时间戳单位
                if timestamp_unit == 'auto':
                    # 自动判断：如果时间戳大于1e10，认为是毫秒单位
                    if ts > 1e10:
                        ts = ts / 1000  # 转为秒
                
                dt = datetime.fromtimestamp(ts)
                return {
                    'timestamp': ts,
                    'datetime': dt.isoformat(),
                    'formatted': dt.strftime('%Y-%m-%d %H:%M:%S'),
                    'timezone': str(dt.astimezone().tzinfo)
                }
            elif convert_type == 'to_timestamp':
                # 日期时间转时间戳
                try:
                    dt = date_parse(timestamp)
                except ValueError:
                    # 如果无法解析，尝试常见格式
                    formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d %H:%M:%S', '%Y/%m/%d']
                    dt = None
                    for fmt in formats:
                        try:
                            dt = datetime.strptime(timestamp, fmt)
                            break
                        except ValueError:
                            continue
                    
                    if dt is None:
                        raise ValueError(f"无法解析日期时间格式: {timestamp}")
                
                timestamp_sec = int(dt.timestamp())
                timestamp_ms = int(dt.timestamp() * 1000)
                
                return {
                    'datetime': timestamp,
                    'timestamp': timestamp_sec,
                    'timestamp_ms': timestamp_ms
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'input': timestamp,
                'convert_type': convert_type
            }

    @staticmethod
    def base_convert(number: str, from_base: int, to_base: int) -> Dict[str, Any]:
        """
        进制转换
        :param number: 数字字符串
        :param from_base: 源进制
        :param to_base: 目标进制
        :return: 转换结果
        """
        try:
            # 将输入数字从源进制转换为十进制
            decimal_num = int(number, from_base)
            
            # 将十进制数转换为目标进制
            if to_base == 2:
                result = bin(decimal_num)[2:]  # 去掉'0b'前缀
            elif to_base == 8:
                result = oct(decimal_num)[2:]  # 去掉'0o'前缀
            elif to_base == 10:
                result = str(decimal_num)
            elif to_base == 16:
                result = hex(decimal_num)[2:].upper()  # 去掉'0x'前缀并转为大写
            else:
                # 通用进制转换
                if to_base < 2 or to_base > 36:
                    raise ValueError("进制必须在2-36之间")
                
                digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                if decimal_num == 0:
                    result = "0"
                else:
                    result = ""
                    while decimal_num > 0:
                        result = digits[decimal_num % to_base] + result
                        decimal_num //= to_base
            
            return {
                'original': number,
                'from_base': from_base,
                'to_base': to_base,
                'result': result,
                'decimal_value': decimal_num
            }
        except ValueError as e:
            return {
                'success': False,
                'error': str(e),
                'original': number,
                'from_base': from_base,
                'to_base': to_base
            }

    @staticmethod
    def base64_encode(text: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Base64编码
        :param text: 待编码文本
        :param encoding: 文本编码
        :return: 编码结果
        """
        try:
            text_bytes = text.encode(encoding)
            encoded_bytes = base64.b64encode(text_bytes)
            encoded_str = encoded_bytes.decode('ascii')
            
            return {
                'original': text,
                'encoded': encoded_str,
                'encoding': encoding
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original': text
            }

    @staticmethod
    def base64_decode(encoded_str: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Base64解码
        :param encoded_str: Base64编码字符串
        :param encoding: 输出文本编码
        :return: 解码结果
        """
        try:
            encoded_bytes = encoded_str.encode('ascii')
            decoded_bytes = base64.b64decode(encoded_bytes)
            decoded_str = decoded_bytes.decode(encoding)
            
            return {
                'encoded': encoded_str,
                'decoded': decoded_str,
                'encoding': encoding
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'encoded': encoded_str
            }

    # ==================== 加密工具 ====================

    @staticmethod
    def md5_hash(text: str) -> Dict[str, Any]:
        """
        MD5哈希
        :param text: 输入文本
        :return: 哈希结果
        """
        try:
            hash_obj = hashlib.md5(text.encode('utf-8'))
            hash_hex = hash_obj.hexdigest()
            
            return {
                'original': text,
                'hash': hash_hex,
                'algorithm': 'md5'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original': text
            }

    @staticmethod
    def sha1_hash(text: str) -> Dict[str, Any]:
        """
        SHA1哈希
        :param text: 输入文本
        :return: 哈希结果
        """
        try:
            hash_obj = hashlib.sha1(text.encode('utf-8'))
            hash_hex = hash_obj.hexdigest()
            
            return {
                'original': text,
                'hash': hash_hex,
                'algorithm': 'sha1'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original': text
            }

    @staticmethod
    def sha256_hash(text: str) -> Dict[str, Any]:
        """
        SHA256哈希
        :param text: 输入文本
        :return: 哈希结果
        """
        try:
            hash_obj = hashlib.sha256(text.encode('utf-8'))
            hash_hex = hash_obj.hexdigest()
            
            return {
                'original': text,
                'hash': hash_hex,
                'algorithm': 'sha256'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original': text
            }

    @staticmethod
    def sha512_hash(text: str) -> Dict[str, Any]:
        """
        SHA512哈希
        :param text: 输入文本
        :return: 哈希结果
        """
        try:
            hash_obj = hashlib.sha512(text.encode('utf-8'))
            hash_hex = hash_obj.hexdigest()
            
            return {
                'original': text,
                'hash': hash_hex,
                'algorithm': 'sha512'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original': text
            }

    @staticmethod
    def hash_comparison(text: str, hash_value: str, algorithm: str = 'md5') -> Dict[str, Any]:
        """
        哈希值比对
        :param text: 原始文本
        :param hash_value: 哈希值
        :param algorithm: 算法类型
        :return: 比对结果
        """
        try:
            # 根据算法计算文本的哈希值
            if algorithm.lower() == 'md5':
                calculated_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
            elif algorithm.lower() == 'sha1':
                calculated_hash = hashlib.sha1(text.encode('utf-8')).hexdigest()
            elif algorithm.lower() == 'sha256':
                calculated_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
            elif algorithm.lower() == 'sha512':
                calculated_hash = hashlib.sha512(text.encode('utf-8')).hexdigest()
            else:
                return {
                    'success': False,
                    'error': f'不支持的算法: {algorithm}',
                    'algorithm': algorithm
                }
            
            is_match = calculated_hash.lower() == hash_value.lower()
            
            return {
                'original_text': text,
                'provided_hash': hash_value,
                'calculated_hash': calculated_hash,
                'algorithm': algorithm,
                'is_match': is_match
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'algorithm': algorithm
            }

    @staticmethod
    def password_strength(password: str) -> Dict[str, Any]:
        """
        密码强度分析
        :param password: 密码
        :return: 强度分析结果
        """
        try:
            import re
            
            score = 0
            feedback = []
            
            # 长度检查
            length = len(password)
            if length >= 8:
                score += 1
            else:
                feedback.append("密码长度至少应为8位")
            
            # 包含小写字母
            if re.search(r'[a-z]', password):
                score += 1
            else:
                feedback.append("密码应包含小写字母")
            
            # 包含大写字母
            if re.search(r'[A-Z]', password):
                score += 1
            else:
                feedback.append("密码应包含大写字母")
            
            # 包含数字
            if re.search(r'\d', password):
                score += 1
            else:
                feedback.append("密码应包含数字")
            
            # 包含特殊字符
            if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                score += 1
            else:
                feedback.append("密码应包含特殊字符")
            
            # 长度加分
            if length >= 12:
                score += 1
            if length >= 16:
                score += 1
            
            # 确定强度等级
            if score <= 2:
                strength = "弱"
            elif score <= 4:
                strength = "中"
            elif score <= 5:
                strength = "强"
            else:
                strength = "很强"
            
            return {
                'password': password,
                'score': score,
                'max_score': 7,
                'strength': strength,
                'feedback': feedback,
                'is_strong': score >= 4
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'password': password
            }

    # ==================== JSON工具 ====================

    @staticmethod
    def format_json(json_str: str, indent: int = 2, sort_keys: bool = False, compress: bool = False) -> Dict[str, Any]:
        """
        格式化JSON
        :param json_str: JSON字符串
        :param indent: 缩进空格数
        :param sort_keys: 是否排序键
        :param compress: 是否压缩（无格式化）
        :return: 格式化结果
        """
        try:
            # 解析JSON
            parsed_json = json.loads(json_str)
            
            if compress:
                # 压缩JSON（无空格）
                result = json.dumps(parsed_json, separators=(',', ':'))
            else:
                # 格式化JSON
                result = json.dumps(parsed_json, indent=indent, sort_keys=sort_keys, ensure_ascii=False)
            
            return {
                'original': json_str,
                'formatted': result,
                'indent': indent,
                'sort_keys': sort_keys,
                'compress': compress
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'JSON格式错误: {str(e)}',
                'original': json_str
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original': json_str
            }

    @staticmethod
    def validate_json(json_str: str) -> Dict[str, Any]:
        """
        验证JSON格式
        :param json_str: JSON字符串
        :return: 验证结果
        """
        try:
            parsed_json = json.loads(json_str)
            return {
                'valid': True,
                'parsed': parsed_json,
                'keys_count': len(parsed_json) if isinstance(parsed_json, dict) else 0,
                'type': type(parsed_json).__name__
            }
        except json.JSONDecodeError as e:
            return {
                'valid': False,
                'error': str(e),
                'error_position': str(e.pos) if hasattr(e, 'pos') else None
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }

    # 添加工具分类和列表方法
    @staticmethod
    def get_tool_list():
        """获取所有工具列表"""
        return [
            # 测试数据工具
            {'name': 'generate_chinese_name', 'display_name': '中文姓名生成器', 'description': '生成随机中文姓名', 'category': 'test_data', 'icon': 'user'},
            {'name': 'generate_chinese_phone', 'display_name': '中文手机号生成器', 'description': '生成随机中文手机号', 'category': 'test_data', 'icon': 'phone'},
            {'name': 'generate_chinese_email', 'display_name': '中文邮箱生成器', 'description': '生成随机中文邮箱', 'category': 'test_data', 'icon': 'message'},
            {'name': 'generate_chinese_address', 'display_name': '中文地址生成器', 'description': '生成随机中文地址', 'category': 'test_data', 'icon': 'location'},
            {'name': 'generate_company_name', 'display_name': '公司名称生成器', 'description': '生成随机公司名称', 'category': 'test_data', 'icon': 'office-building'},
            
            # 字符工具
            {'name': 'remove_whitespace', 'display_name': '去除空格换行', 'description': '去除字符串中的空格和换行符', 'category': 'string', 'icon': 'delete'},
            {'name': 'replace_string', 'display_name': '字符串替换', 'description': '替换字符串中的内容', 'category': 'string', 'icon': 'edit'},
            {'name': 'escape_string', 'display_name': '字符串转义', 'description': '将字符串进行转义处理', 'category': 'string', 'icon': 'lock'},
            {'name': 'unescape_string', 'display_name': '字符串反转义', 'description': '将转义字符串还原', 'category': 'string', 'icon': 'unlock'},
            {'name': 'word_count', 'display_name': '字数统计', 'description': '统计字符串的字数和字符数', 'category': 'string', 'icon': 'data-line'},
            {'name': 'text_diff', 'display_name': '文本对比', 'description': '对比两段文本的差异', 'category': 'string', 'icon': 'document-copy'},
            {'name': 'regex_test', 'display_name': '正则测试', 'description': '测试正则表达式的匹配结果', 'category': 'string', 'icon': 'search'},
            {'name': 'case_convert', 'display_name': '大小写转换', 'description': '转换字符串的大小写', 'category': 'string', 'icon': 'sort'},
            {'name': 'string_format', 'display_name': '字符串格式化', 'description': '格式化字符串', 'category': 'string', 'icon': 'edit'},
            
            # 随机工具
            {'name': 'random_int', 'display_name': '随机整数', 'description': '生成指定范围的随机整数', 'category': 'random', 'icon': 'sort'},
            {'name': 'random_float', 'display_name': '随机浮点数', 'description': '生成指定范围的随机浮点数', 'category': 'random', 'icon': 'sort'},
            {'name': 'random_string', 'display_name': '随机字符串', 'description': '生成指定长度的随机字符串', 'category': 'random', 'icon': 'sort'},
            {'name': 'random_uuid', 'display_name': '随机UUID', 'description': '生成随机UUID(GUID)', 'category': 'random', 'icon': 'sort'},
            {'name': 'random_boolean', 'display_name': '随机布尔值', 'description': '生成随机布尔值', 'category': 'random', 'icon': 'sort'},
            {'name': 'random_mac_address', 'display_name': '随机MAC地址', 'description': '生成随机MAC地址', 'category': 'random', 'icon': 'sort'},
            {'name': 'random_ip_address', 'display_name': '随机IP地址', 'description': '生成随机IP地址(IPv4/IPv6)', 'category': 'random', 'icon': 'sort'},
            {'name': 'random_date', 'display_name': '随机日期', 'description': '生成指定范围内的随机日期', 'category': 'random', 'icon': 'clock'},
            {'name': 'random_password', 'display_name': '随机密码', 'description': '生成随机密码(包含大小写、数字、特殊字符)', 'category': 'random', 'icon': 'lock'},
            {'name': 'random_color', 'display_name': '随机颜色', 'description': '生成随机颜色数据', 'category': 'random', 'icon': 'picture'},
            {'name': 'random_sequence', 'display_name': '随机序列数据', 'description': '生成随机序列数据', 'category': 'random', 'icon': 'sort'},
            
            # 编码工具
            {'name': 'timestamp_convert', 'display_name': '时间戳转换', 'description': '时间戳与日期时间相互转换', 'category': 'encoding', 'icon': 'clock'},
            {'name': 'base_convert', 'display_name': '进制转换', 'description': '不同进制之间的转换', 'category': 'encoding', 'icon': 'sort'},
            {'name': 'base64_encode', 'display_name': 'Base64编码', 'description': '使用Base64算法加密数据', 'category': 'encoding', 'icon': 'lock'},
            {'name': 'base64_decode', 'display_name': 'Base64解码', 'description': '使用Base64算法解密数据', 'category': 'encoding', 'icon': 'unlock'},
            
            # 加密工具
            {'name': 'md5_hash', 'display_name': 'MD5加密', 'description': '生成MD5哈希值', 'category': 'encryption', 'icon': 'lock'},
            {'name': 'sha1_hash', 'display_name': 'SHA1加密', 'description': '生成SHA1哈希值', 'category': 'encryption', 'icon': 'lock'},
            {'name': 'sha256_hash', 'display_name': 'SHA256加密', 'description': '生成SHA256哈希值', 'category': 'encryption', 'icon': 'lock'},
            {'name': 'sha512_hash', 'display_name': 'SHA512加密', 'description': '生成SHA512哈希值', 'category': 'encryption', 'icon': 'lock'},
            {'name': 'hash_comparison', 'display_name': '哈希值比对', 'description': '比对两个哈希值是否相同', 'category': 'encryption', 'icon': 'sort'},
            {'name': 'password_strength', 'display_name': '密码强度分析', 'description': '分析密码的强度', 'category': 'encryption', 'icon': 'view'},
            
            # JSON工具
            {'name': 'format_json', 'display_name': 'JSON格式化', 'description': '格式化或压缩JSON数据', 'category': 'json', 'icon': 'list'},
            {'name': 'validate_json', 'display_name': 'JSON校验', 'description': '验证JSON格式的正确性', 'category': 'json', 'icon': 'circle-check'},
        ]

    @staticmethod
    def get_categories():
        """获取所有工具分类"""
        return [
            {'category': 'test_data', 'name': '测试数据', 'icon': 'user'},
            {'category': 'json', 'name': 'JSON工具', 'icon': 'edit'},
            {'category': 'string', 'name': '字符工具', 'icon': 'document'},
            {'category': 'encoding', 'name': '编码工具', 'icon': 'code'},
            {'category': 'random', 'name': '随机工具', 'icon': 'distribute'},
            {'category': 'encryption', 'name': '加密工具', 'icon': 'lock'},
            {'category': 'crontab', 'name': 'Crontab工具', 'icon': 'clock'},
        ]