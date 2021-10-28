import org.apache.spark.sql.{DataFrame, Encoders, SparkSession, functions}
import org.apache.spark.sql.functions.{array_contains, length}


object Exercice1 extends App  {
  /// créer une classe de cas Sort avec des paramètres name, level.....
  case class Sort(name: String, level: Int,wizard:Boolean,spell_resistance:Boolean,components:Array[String]) {}

  /// définir une sparkSession avec plusieurs méthodes builder(),master()..... pour créer un Dataframe et utiliser des fonctions spark
  val spark = SparkSession
    .builder() //créer une nouvelle SparkSession
    .master("local[*]")
    .appName("Spark SQL basic example") //définir le nom de l'application
    .config("spark.some.config.option", "some-value")
    .getOrCreate() //créer ou renvoyer un objet sparkSession

  import spark.implicits._

  // pour désactiver les messages des érreurs
  spark.sparkContext.setLogLevel("ERROR")

  // créer un schema spark à partir de la structure de notre class case Sort
  val schema = Encoders.product[Sort].schema

  // la lecture du fichier json et convertion en dataSet a partir de la classe Sort
  val SortDS = spark.read.schema(schema).json("src/main/resources/LastJson.json").as[Sort]

  // utiliser la fonction filter() pour trier les sorts de notre dataSet
     SortDS.filter(SortDS("wizard")=== true && SortDS("level")<= 4
       && array_contains(SortDS("components")," V")
       && (functions.size(SortDS("components"))===1 )  )
    // afficher la requête
    .show(SortDS.count.toInt,false)


  // créer un dataFrame à partir de json
  val multiline_df: DataFrame = spark.read.json("src/main/resources/LastJson.json")

  //CreateOrReplaceTempView crée une table avec le nom sortDf
  multiline_df.createOrReplaceTempView("SortDF")

  // Requête  sql
  val SortDFSQL = spark.sql(" SELECT * FROM SortDF WHERE level <=4 AND wizard= true  " +
    "AND components[0] like '%V%' AND size(components)=1"    )
  SortDFSQL.show(SortDFSQL.count.toInt,false)
  multiline_df.printSchema()


}
