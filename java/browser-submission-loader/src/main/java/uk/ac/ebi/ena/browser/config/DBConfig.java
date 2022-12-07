package uk.ac.ebi.ena.browser.config;

import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.autoconfigure.jdbc.DataSourceProperties;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.core.env.Environment;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jmx.export.MBeanExporter;

import javax.sql.DataSource;

@Configuration
@Slf4j
public class DBConfig {

    private final Environment environment;

    @Resource
    private ObjectProvider<MBeanExporter> mBeanExporter;

    public DBConfig(Environment environment) {
        this.environment = environment;
    }

    @Bean
    @Primary
    @ConfigurationProperties("ds.erapro")
    public DataSourceProperties eraproDataSourceProperties() {
        return new DataSourceProperties();
    }

    @Bean(name = "dsErapro")
    @Primary
    @ConfigurationProperties(prefix = "ds.erapro.configuration")
    public DataSource eraproDataSource() {
        // Hikari registers the datasource MXBean (ds.erapro.configuration.register-mbeans=true)
        // so excluded the dsErapro datasource from Spring's JMX to avoid duplication exception during runtime
        mBeanExporter.ifUnique((exporter) -> exporter.addExcludedBean("dsErapro"));
        return eraproDataSourceProperties().initializeDataSourceBuilder().build();
    }

    @Primary
    @Bean(name = "jdbcErapro")
    @Autowired
    public JdbcTemplate eraproJdbcTemplate(@Qualifier("dsErapro") DataSource ds) {
        JdbcTemplate jdbcTemplate = new JdbcTemplate(ds);
        jdbcTemplate.setFetchSize(environment.getProperty("ds.erapro.fetchSize", Integer.class, 1000));
        log.debug("jdbcErapro object");
        return jdbcTemplate;
    }

    @Bean(name = "jdbcEtapro")
    @Autowired
    public JdbcTemplate etaproJdbcTemplate(@Qualifier("dsEtapro") DataSource ds) {
        return new JdbcTemplate(ds);
    }

    @Bean
    @ConfigurationProperties("ds.etapro")
    public DataSourceProperties etaproDataSourceProperties() {
        return new DataSourceProperties();
    }

    @ConfigurationProperties(prefix = "ds.etapro.configuration")
    @Bean(name = "dsEtapro")
    public DataSource etaproDataSource() {
        // Hikari registers the datasource MXBean (ds.etapro.configuration.register-mbeans=true)
        // so excluded the dsEtapro datasource from Spring's JMX to avoid duplication exception during runtime
        mBeanExporter.ifUnique((exporter) -> exporter.addExcludedBean("dsEtapro"));
        return etaproDataSourceProperties().initializeDataSourceBuilder().build();
    }
}
