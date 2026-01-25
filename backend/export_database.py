import pymysql
import os
from datetime import datetime

def export_database():
    # 从环境变量获取数据库配置
    MYSQL_HOST = '192.168.40.128'
    MYSQL_PORT = 3306
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '123321'
    MYSQL_DATABASE = 'testcase_generator'

    # 连接数据库
    connection = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        charset='utf8mb4'
    )

    try:
        cursor = connection.cursor()

        # 获取所有表名
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        print(f"获取到的表: {tables}")

        sql_content = []
        sql_content.append(f"-- 数据库导出文件")
        sql_content.append(f"-- 数据库: {MYSQL_DATABASE}")
        sql_content.append(f"-- 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sql_content.append(f"-- 说明: 包含所有表的建表语句和数据(除operation_logs表无数据)")
        sql_content.append("\nSET NAMES utf8mb4;")
        sql_content.append("SET FOREIGN_KEY_CHECKS = 0;")
        sql_content.append("\n")

        # 遍历每个表
        for table_tuple in tables:
            table = table_tuple[0]
            print(f"正在处理表: {table}")

            # 获取建表语句
            cursor.execute(f"SHOW CREATE TABLE `{table}`")
            create_table_result = cursor.fetchone()
            create_table_sql = create_table_result[1]

            sql_content.append(f"-- 表结构: {table}")
            sql_content.append("DROP TABLE IF EXISTS `" + table + "`;")
            sql_content.append(create_table_sql + ";\n")

            # 判断是否需要导出数据
            if table == 'operation_logs':
                sql_content.append(f"-- 表 {table} 的数据不导出\n")
            else:
                # 获取表数据
                cursor.execute(f"SELECT * FROM `{table}`")
                rows = cursor.fetchall()

                if rows:
                    # 获取列名
                    cursor.execute(f"DESCRIBE `{table}`")
                    columns = [col[0] for col in cursor.fetchall()]

                    sql_content.append(f"-- 表数据: {table}")
                    sql_content.append(f"INSERT INTO `{table}` ({', '.join(columns)}) VALUES")

                    insert_values = []
                    for row in rows:
                        values = []
                        for value in row:
                            if value is None:
                                values.append('NULL')
                            elif isinstance(value, (int, float)):
                                values.append(str(value))
                            else:
                                # 转义特殊字符
                                escaped_value = str(value).replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"')
                                values.append(f"'{escaped_value}'")

                        insert_values.append(f"({', '.join(values)})")

                    # 分批插入，每100条一个INSERT语句
                    batch_size = 100
                    for i in range(0, len(insert_values), batch_size):
                        batch = insert_values[i:i + batch_size]
                        sql_content.append(',\n'.join(batch) + ';')

                    sql_content.append("\n")

        sql_content.append("SET FOREIGN_KEY_CHECKS = 1;")

        # 写入文件
        output_file = 'database_export.sql'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_content))

        print(f"\n数据库导出完成！")
        print(f"导出文件: {output_file}")
        print(f"共处理 {len(tables)} 个表")

    except Exception as e:
        print(f"导出过程中出现错误: {str(e)}")
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    export_database()
